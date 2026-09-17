"""Browser MuJoCo collection, separated from CLI parsing and recording storage."""

import asyncio
import tempfile
from importlib.metadata import version

from ..demos import DemoRecorder
from .bundle import export_bundle


def frame_time(frame, model):
    """Post-step state time for Vuer 0.1.6's bundled AutoSimLoop.

    mj_step samples the clock before integrating. This client emits immediately
    after the last step, without mj_forward, so the state is one timestep later.
    ON_MUJOCO_LOAD and other clients do not share this contract.
    """
    sensors = frame["sensordata"]
    if len(sensors) != model.nsensordata + 1:
        raise ValueError("Browser frame is missing the recording clock sensor")
    return float(sensors[-1]) + float(model.opt.timestep)


def collect(
    env,
    scene_name,
    output,
    *,
    host="127.0.0.1",
    port=8012,
    public_url=None,
    right_actuator=None,
    left_actuator=None,
    fps=50,
    max_frames=30000,
):
    try:
        from vuer import Vuer
        from vuer.schemas import Box, DefaultScene, HandActuator, Html, MuJoCo, span
    except ImportError as exc:
        raise ImportError("Recording requires the teleop extra: uv sync --extra teleop") from exc
    if version("vuer") != "0.1.6":
        raise ValueError("Recording requires Vuer 0.1.6 and its bundled browser client; sync the teleop extra")

    recorder = DemoRecorder(env, scene_name, max_frames=max_frames)
    recorder.metadata.update(
        vuer_version="0.1.6",
        browser_mujoco_version="3.3.6",
        clock="pre-integration-sensor-plus-timestep",
    )
    initial = env.frame()
    controls = []
    for hand, name in (("right", right_actuator), ("left", left_actuator)):
        if name is None:
            continue
        index = env.model.actuator(name).id
        low, high = env.action_space["ctrl"].low[index], env.action_space["ctrl"].high[index]
        if not (float("-inf") < low < high < float("inf")):
            raise ValueError("Hand-controlled actuators require finite, distinct ctrl limits")
        scale = -12 * (high - low)
        controls.append(
            HandActuator(
                key=f"{hand}-pinch",
                ctrlId=index,
                cond=f"{hand}-squeeze",
                value=f"{hand}:thumb-tip,{hand}:index-finger-tip",
                offset=0.1 - low / scale,
                scale=scale,
                low=float(low),
                high=float(high),
            )
        )

    with tempfile.TemporaryDirectory(prefix="lucidxr-vuer-") as directory:
        files = export_bundle(env.scene, directory, recording=True)
        url = (public_url or f"http://localhost:{port}").rstrip("/")
        app = Vuer(workspace=directory, host=host, port=port, free_port=False)
        owner = None
        loaded = False
        recording = False
        last_error = None

        def component():
            return MuJoCo(
                *controls,
                key="demo-sim",
                src=f"{url}/workspace/scene.xml",
                assets=[f"{url}/workspace/{name}" for name in files if name != "scene.xml"],
                frameKeys=" ".join((*recorder.shapes, "sensordata")),
                useDrag=False,
                fps=fps,
                pause=False,
                **{name: values.ravel().tolist() for name, values in initial.items()},
            )

        def status(session, message):
            session.upsert @ Html(span(message), key="record-status", position=[0, 1.7, -1])
            print(message, flush=True)

        def save():
            path = recorder.save(output)
            if path is not None:
                print(f"Saved {path}", flush=True)
            return path

        @app.add_handler("ON_MUJOCO_LOAD")
        async def on_load(event, session):
            nonlocal loaded
            if session.CURRENT_WS_ID == owner:
                loaded = True
                status(session, "Ready. Blue: start/stop + save. Red: discard.")

        @app.add_handler("ON_MUJOCO_FRAME")
        async def on_frame(event, session):
            nonlocal recording, last_error
            if session.CURRENT_WS_ID != owner or not recording:
                return
            try:
                frame = event.value["keyFrame"]
                recorder.append(frame, frame_time(frame, env.model))
                if len(recorder.frames) == recorder.max_frames:
                    recording = False
                    save()
                    status(session, "Frame limit reached; saved. Blue starts another recording.")
            except (KeyError, TypeError, ValueError, OSError) as exc:
                recording = False
                last_error = exc
                status(session, f"Recording stopped: {exc}. Existing frames retained; blue retries save.")

        @app.add_handler("ON_CLICK")
        async def on_click(event, session):
            nonlocal recording, last_error
            if session.CURRENT_WS_ID != owner or not loaded:
                return
            key = event.value.get("key", getattr(event, "key", None))
            if key == "discard-demo":
                recording = False
                recorder.clear()
                last_error = None
                status(session, "Discarded. Blue starts another recording.")
            elif key == "record-demo":
                try:
                    if recording or recorder.frames:
                        recording = False
                        save()
                        last_error = None
                        status(session, "Saved. Blue starts another recording.")
                    else:
                        recording = True
                        status(session, "Recording. Blue saves; red discards.")
                except OSError as exc:
                    last_error = exc
                    status(session, f"Save failed: {exc}. Frames retained; blue retries.")
            elif key == "reset-demo":
                if recording or recorder.frames:
                    status(session, "Save or discard before resetting the scene.")
                else:
                    session.update @ MuJoCo(
                        key="demo-sim", **{name: value.ravel().tolist() for name, value in initial.items()}
                    )
                    status(session, "Scene state reset.")

        @app.spawn
        async def connected(session):
            nonlocal owner, loaded, recording
            if owner is not None:
                status(session, "Another client owns this recording session.")
                return
            owner = session.CURRENT_WS_ID
            loaded = False
            try:
                session.set @ DefaultScene()
                session.upsert @ component()
                for key, color, x, label in (
                    ("record-demo", "#238aff", -0.35, "Record / save"),
                    ("discard-demo", "#e54b4b", 0, "Discard"),
                    ("reset-demo", "#55aa55", 0.35, "Reset scene"),
                ):
                    session.upsert @ Box(
                        key=key, args=[0.2, 0.2, 0.2], position=[x, 1.3, -1], material={"color": color}
                    )
                    session.upsert @ Html(span(label), key=f"{key}-label", position=[x, 1.5, -1])
                status(session, "Loading scene…")
                while session.CURRENT_WS_ID in app.ws:
                    await asyncio.sleep(0.25)
            finally:
                recording = False
                # Unfinished frames remain in memory for shutdown save or reconnect.
                owner = None
                loaded = False

        print(f"Open {url}. For a headset, supply a reachable HTTPS --public-url.", flush=True)
        try:
            app.start()
        finally:
            if recorder.frames:
                try:
                    save()
                except OSError as exc:
                    raise RuntimeError(f"Unable to save unfinished recording to {output}: {exc}") from exc
            if last_error is not None:
                print(f"Last recording error: {last_error}", flush=True)
