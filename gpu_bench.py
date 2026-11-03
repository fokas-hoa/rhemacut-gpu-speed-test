"""RhemaCut GPU speed test (DirectML).

Measures how fast this computer runs the speech-alignment model that RhemaCut
uses, first on the processor (CPU) and then on every graphics card through
Microsoft DirectML, and checks that every device produces the same result.

What it does, and nothing else:
- creates five 30-second test sounds in memory (synthetic, generated from fixed
  numbers by this file; no recordings, no microphone);
- runs data/greek-ctc.onnx on them with ONNX Runtime;
- writes one RESULT-<date>-<time>.json file next to this script.
It does not use the network, install anything, change settings, or read any
file outside its own folder. The RESULT file contains the Windows version,
processor and graphics card names, and the timings. No user or computer name.

Run "Run speed test.cmd", or: python\\python.exe gpu_bench.py
"""
import ctypes as c
import datetime, hashlib, json, os, platform, sys, time, uuid
from pathlib import Path

VERSION = "1.0.0"
HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
GRAPH = DATA / "greek-ctc.onnx"
GRAPH_SHA256 = "cac76a7f59023909d47690aafb98f756dfccafc70f49482d63c5d89ad437703f"
REFERENCE = DATA / "reference.npz"
WINDOWS = 5
SAMPLE_RATE = 16000
SECONDS = 30
REPEATS = 3
MATCH_FRAMES = 15  # up to 1% of 1499 frames may differ on near-ties between devices


def say(text=""):
    print(text, flush=True)


def test_sound(index):
    """Deterministic speech-like sound: voiced 'syllables' with harmonics,
    pitch movement, pauses and light noise. Generated, not recorded."""
    import numpy as np
    rng = np.random.default_rng(20261103 + index)
    n = SAMPLE_RATE * SECONDS
    t = np.arange(n) / SAMPLE_RATE
    signal = np.zeros(n)
    position = 0.2
    while position < SECONDS - 0.5:
        length = rng.uniform(0.12, 0.35)
        start, end = int(position * SAMPLE_RATE), int(min(SECONDS, position + length) * SAMPLE_RATE)
        seg_t = t[start:end] - t[start]
        f0 = rng.uniform(95, 230) * (1 + 0.15 * np.sin(2 * np.pi * rng.uniform(1, 4) * seg_t))
        phase = 2 * np.pi * np.cumsum(f0) / SAMPLE_RATE
        voiced = sum((0.8 ** k) * np.sin(k * phase) for k in range(1, 12))
        envelope = np.sin(np.pi * np.linspace(0, 1, end - start)) ** 2
        signal[start:end] += voiced * envelope
        position += length + (rng.uniform(0.3, 0.9) if rng.random() < 0.15 else rng.uniform(0.02, 0.08))
    signal += 0.02 * rng.standard_normal(n)
    signal = signal / np.max(np.abs(signal)) * 0.5
    signal = (signal - signal.mean()) / (signal.std() + 1e-7)  # same normalisation as the model's processor
    return signal.astype(np.float32)[None, :]


def adapters():
    """Lists graphics adapters with Windows DXGI (read-only)."""
    class GUID(c.Structure):
        _fields_ = [("Data1", c.c_uint32), ("Data2", c.c_uint16), ("Data3", c.c_uint16), ("Data4", c.c_ubyte * 8)]

    class LUID(c.Structure):
        _fields_ = [("LowPart", c.c_uint32), ("HighPart", c.c_int32)]

    class DESC(c.Structure):
        _fields_ = [("Description", c.c_wchar * 128), ("VendorId", c.c_uint32), ("DeviceId", c.c_uint32),
                    ("SubSysId", c.c_uint32), ("Revision", c.c_uint32), ("DedicatedVideoMemory", c.c_size_t),
                    ("DedicatedSystemMemory", c.c_size_t), ("SharedSystemMemory", c.c_size_t), ("AdapterLuid", LUID)]

    def method(obj, index, result, *args):
        table = c.cast(obj, c.POINTER(c.POINTER(c.c_void_p))).contents
        return c.WINFUNCTYPE(result, c.c_void_p, *args)(table[index])

    factory = c.c_void_p()
    iid = GUID.from_buffer_copy(uuid.UUID("7b7166ec-21c7-44ae-b21a-c9ae321ae369").bytes_le)  # IDXGIFactory
    create = c.WinDLL("dxgi.dll").CreateDXGIFactory
    create.argtypes = [c.POINTER(GUID), c.POINTER(c.c_void_p)]
    create.restype = c.c_long
    if create(c.byref(iid), c.byref(factory)) != 0:
        return []
    rows = []
    try:
        for index in range(16):
            adapter = c.c_void_p()
            hr = method(factory, 7, c.c_long, c.c_uint, c.POINTER(c.c_void_p))(factory, index, c.byref(adapter))
            if hr & 0xFFFFFFFF == 0x887A0002:  # DXGI_ERROR_NOT_FOUND: no more adapters
                break
            try:
                desc = DESC()
                method(adapter, 8, c.c_long, c.POINTER(DESC))(adapter, c.byref(desc))
                rows.append({"index": index, "name": desc.Description, "vendorId": desc.VendorId,
                             "dedicatedVideoMB": desc.DedicatedVideoMemory // 2**20})
            finally:
                method(adapter, 2, c.c_ulong)(adapter)
    finally:
        method(factory, 2, c.c_ulong)(factory)
    return rows


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def session_for(ort, providers):
    opts = ort.SessionOptions()
    if providers[0] != "CPUExecutionProvider":
        opts.enable_mem_pattern = False
        opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    return ort.InferenceSession(str(GRAPH), sess_options=opts, providers=providers)


def make_reference():
    """Maintainer step: computes data/reference.npz on the CPU."""
    import numpy as np
    import onnxruntime as ort
    session = session_for(ort, ["CPUExecutionProvider"])
    name = session.get_inputs()[0].name
    logits = [session.run(None, {name: test_sound(i)})[0][0] for i in range(WINDOWS)]
    np.savez(REFERENCE, logits=np.stack(logits).astype(np.float16))
    say(f"wrote {REFERENCE.name}")


def main():
    import numpy as np
    import onnxruntime as ort
    ort.set_default_logger_severity(3)

    say(f"RhemaCut GPU speed test {VERSION}. This takes a few minutes; please keep this window open.")
    say("Checking files...")
    if sha256(GRAPH) != GRAPH_SHA256:
        raise RuntimeError("data/greek-ctc.onnx is damaged or changed. Please download the release again.")
    reference = np.load(REFERENCE)["logits"].astype(np.float32)
    sounds = [test_sound(i) for i in range(WINDOWS)]

    cpu_name = platform.processor()
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
        cpu_name = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
    except OSError:
        pass
    gpus = adapters()
    report = {"tool": f"RhemaCut GPU speed test {VERSION}",
              "atUtc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "windows": platform.platform(), "cpu": cpu_name, "cpuThreads": os.cpu_count(), "gpus": gpus,
              "onnxruntime": ort.__version__, "repeats": REPEATS, "runs": []}

    targets, seen = [("CPU", ["CPUExecutionProvider"], None)], set()
    for g in gpus:  # vendor 0x1414 = Microsoft Basic Render Driver (software); skip repeated listings
        if g["vendorId"] != 0x1414 and g["name"] not in seen:
            seen.add(g["name"])
            targets.append((g["name"], [("DmlExecutionProvider", {"device_id": str(g["index"])})], g["index"]))

    for label, providers, index in targets:
        say(f"\nTesting {label} ...")
        run = {"device": label, "backend": "CPU" if index is None else "DirectML", "dxgiIndex": index, "windows": []}
        try:
            t = time.perf_counter()
            session = session_for(ort, providers)
            run["loadSeconds"] = round(time.perf_counter() - t, 2)
            run["providers"] = session.get_providers()
            name = session.get_inputs()[0].name
            for i, sound in enumerate(sounds):
                s = time.perf_counter()
                logits = session.run(None, {name: sound})[0][0]
                first = time.perf_counter() - s
                times = []
                for _ in range(REPEATS):
                    s = time.perf_counter()
                    logits = session.run(None, {name: sound})[0][0]
                    times.append(time.perf_counter() - s)
                diff = int((logits.argmax(-1) != reference[i].argmax(-1)).sum())
                run["windows"].append({"window": i + 1, "firstSeconds": round(first, 3),
                                       "medianSeconds": round(float(np.median(times)), 3),
                                       "framesDifferent": diff,
                                       "maxLogitDifference": round(float(np.abs(logits - reference[i]).max()), 4)})
                say(f"  test sound {i + 1}: {np.median(times):.2f} s for 30 s of audio, differing frames {diff}")
            run["medianSecondsPer30s"] = round(float(np.median([w["medianSeconds"] for w in run["windows"]])), 3)
            run["resultsMatch"] = all(w["framesDifferent"] <= MATCH_FRAMES for w in run["windows"])
            run["status"] = "OK"
        except Exception as error:  # record the failure and continue with the next device
            run["status"] = "FAILED"
            run["error"] = f"{type(error).__name__}: {error}"[:500]
            say(f"  failed: {run['error']}")
        report["runs"].append(run)

    out = HERE / f"RESULT-{datetime.datetime.now():%Y%m%d-%H%M%S}.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    say("\nSummary (seconds per 30 seconds of audio, lower is faster):")
    for run in report["runs"]:
        match = "" if run["status"] != "OK" else ("  results match" if run["resultsMatch"] else "  RESULTS DIFFER")
        say(f"  {run['device']}: {run.get('medianSecondsPer30s', run['status'])}{match}")
    say(f"\nDone. Please send this file back:\n  {out.name}\n(it is in the same folder as this program)")


if __name__ == "__main__":
    if "--make-reference" in sys.argv:
        make_reference()
        sys.exit(0)
    try:
        main()
    except Exception as error:
        say(f"\nThe test stopped: {type(error).__name__}: {error}")
    input("\nPress Enter to close this window.")
