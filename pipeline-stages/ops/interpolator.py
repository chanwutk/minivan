import json

import numpy as np

from minivan.dtypes import DetArray, InPipe, Array, S4, OutPipe


def interpolate_trajectory(trajectory: list[tuple[int, Array[S4, np.floating]]], nxt: tuple[int, Array[S4, np.floating]]):
    extend: list[tuple[int, Array[S4, np.floating]]] = []
    if len(trajectory) != 0:
        prv = trajectory[-1]
        assert prv[0] < nxt[0]
        prv_det = prv[1]
        nxt_det = nxt[1]
        dif_det = nxt_det - prv_det
        dif_det = dif_det.reshape(1, -1)

        scale = np.arange(nxt[0] - prv[0], dtype=np.floating).reshape(-1, 1) / (nxt[0] - prv[0])
        
        int_dets = (scale @ dif_det) + prv_det.reshape(1, -1)

        for idx, int_det in enumerate(int_dets[:-1]):
            extend.append((prv[0] + idx + 1, int_det))
    extend.append(nxt)

    trajectory.extend(extend)
    return extend


def interpolate(
    trackQueue: InPipe[tuple[int, DetArray]],
    itrackQueue: OutPipe[tuple[int, list[list[float | int]]]],
    outFile: str,
):
    trajectories: dict[int, list[tuple[int, Array[S4, np.floating]]]] = dict()
    render: dict[int, list[tuple[Array[S4, np.floating], int]]] = dict()
    while True:
        track = trackQueue.get()
        if track is None:
            break

        idx, track = track

        boxes = track[:, :4]
        trackIds = track[:, 4]
        for box, trackId in zip(boxes, trackIds):
            trackId = int(trackId)
            if trackId not in trajectories:
                trajectories[trackId] = []
            extend = interpolate_trajectory(trajectories[trackId], (idx, box))

            for e in extend:
                if e[0] not in render:
                    render[e[0]] = []
                render[e[0]].append((e[1], trackId))
    
    with open(outFile, 'w') as f:
        prevIdx = -1
        for idx, boxes in sorted(render.items()):
            # assert idx == prevIdx + 1, (prevIdx, idx)
            boxes = [[trackId, *box] for box, trackId in boxes]
            itrackQueue.put((idx, boxes))
            f.write(json.dumps((idx, boxes)) + '\n')
            prevIdx = idx
    itrackQueue.put(None)
