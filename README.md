# RhemaCut GPU speed test

*Ελληνικά παρακάτω.*

A small, open test that measures how fast a Windows PC runs the speech-alignment model used by
[RhemaCut](https://www.rhemacut.com), on the processor (CPU) and on each graphics card through
Microsoft DirectML. We use the results to decide whether GPU acceleration is worth adding for
AMD and Intel graphics cards.

## What it runs

- `Run speed test.cmd` starts `gpu_bench.py` with the Python that is inside the download. It contains
  three commands; read it before running.
- `gpu_bench.py` (about 220 lines, readable):
  1. checks the SHA-256 of the model file;
  2. **generates five 30-second synthetic test sounds in memory** (no recordings, no microphone);
  3. runs the model on the CPU, then on every graphics card that Windows lists, 1 + 3 times per sound;
  4. compares each device's output with the reference output computed on a CPU;
  5. writes `RESULT-<date>-<time>.json` next to itself.

It does **not** use the network, install anything, change any setting, or read files outside its own
folder. No administrator rights are needed. Delete the folder to remove it completely.

## What the RESULT file contains

Windows version, processor name and thread count, graphics card names and video memory, ONNX Runtime
version, and the timings and match counts. **No user name, computer name, files or personal data.**
Open it in Notepad before sending it.

## How to run

1. Download `RhemaCut-GPU-Speed-Test-v1.0.0.zip` from the [latest release](../../releases/latest).
2. Optional: check it. In PowerShell: `Get-FileHash .\RhemaCut-GPU-Speed-Test-v1.0.0.zip` must print
   `eae973cf6296cc60cab522b82e01e9cc49d166c44b47dcb71744eb475d7b7c35`.
   After extracting, every file is listed with its SHA-256 in `MANIFEST.sha256`.
3. Extract the zip, open the folder and double-click `Run speed test.cmd`.
   Windows may show "Windows protected your PC" because the file is not signed: click
   **More info**, then **Run anyway**.
4. Wait a few minutes until the window says **Done**, then send the `RESULT-....json` file back.

Requirements: Windows 10 or 11 (64-bit), about 3 GB of free memory, 1.5 GB of disk space.

## What is in the release zip

| Path | What it is | Licence |
|---|---|---|
| `gpu_bench.py`, `Run speed test.cmd` | the test (same files as in this repository) | MIT (`LICENSE`) |
| `python/` | official CPython 3.12.10 Windows embeddable runtime (signed by the Python Software Foundation), without SSL, SQLite and Tk | PSF (`licenses/Python-3.12-LICENSE.txt`) |
| `python/Lib/site-packages/numpy` | NumPy 2.4.6 from PyPI | BSD-3-Clause and bundled notices (`licenses/numpy-2.4.6/`) |
| `python/Lib/site-packages/onnxruntime` | ONNX Runtime DirectML 1.24.4 from PyPI, including Microsoft DirectML 1.15.4 | MIT, third-party notices, DirectML licence (`licenses/`) |
| `data/greek-ctc.onnx` | wav2vec2 XLSR-53 Greek model converted to ONNX | Apache-2.0 (`licenses/MODEL-NOTICE.md`) |
| `data/reference.npz` | reference model output for the five synthetic sounds | MIT |

All third-party files are unmodified copies of the published packages.

---

# Δοκιμή ταχύτητας GPU του RhemaCut

Μια μικρή, ανοιχτή δοκιμή που μετράει πόσο γρήγορα ένας υπολογιστής με Windows τρέχει το μοντέλο
συγχρονισμού λέξεων του [RhemaCut](https://www.rhemacut.com): στον επεξεργαστή (CPU) και σε κάθε κάρτα
γραφικών μέσω Microsoft DirectML. Με τα αποτελέσματα αποφασίζουμε αν αξίζει επιτάχυνση για κάρτες AMD και Intel.

## Τι εκτελεί

- Το `Run speed test.cmd` ξεκινά το `gpu_bench.py` με την Python που υπάρχει μέσα στο zip. Έχει τρεις εντολές· διάβασέ το πριν το τρέξεις.
- Το `gpu_bench.py`:
  1. ελέγχει το SHA-256 του μοντέλου·
  2. **δημιουργεί στη μνήμη πέντε συνθετικούς ήχους 30 δευτερολέπτων** (καμία ηχογράφηση, κανένα μικρόφωνο)·
  3. τρέχει το μοντέλο στον επεξεργαστή και σε κάθε κάρτα γραφικών·
  4. συγκρίνει το αποτέλεσμα κάθε συσκευής με το αποτέλεσμα αναφοράς·
  5. γράφει το αρχείο `RESULT-<ημερομηνία>-<ώρα>.json` δίπλα του.

**Δεν** χρησιμοποιεί δίκτυο, δεν εγκαθιστά τίποτα, δεν αλλάζει ρυθμίσεις και δεν διαβάζει αρχεία έξω από τον φάκελό του.
Δεν χρειάζεται δικαιώματα διαχειριστή. Για να το αφαιρέσεις, σβήνεις τον φάκελο.

## Τι περιέχει το RESULT

Έκδοση Windows, όνομα επεξεργαστή και πλήθος νημάτων, ονόματα καρτών γραφικών και μνήμη τους, έκδοση ONNX Runtime,
χρόνους και ελέγχους ταύτισης. **Κανένα όνομα χρήστη ή υπολογιστή, κανένα αρχείο ή προσωπικό δεδομένο.**
Μπορείς να το ανοίξεις με το Σημειωματάριο πριν το στείλεις.

## Πώς τρέχει

1. Κατέβασε το `RhemaCut-GPU-Speed-Test-v1.0.0.zip` από το [τελευταίο release](../../releases/latest).
2. Προαιρετικά, έλεγξέ το στο PowerShell: `Get-FileHash .\RhemaCut-GPU-Speed-Test-v1.0.0.zip` πρέπει να δώσει `eae973cf6296cc60cab522b82e01e9cc49d166c44b47dcb71744eb475d7b7c35`.
3. Αποσυμπίεσε, άνοιξε τον φάκελο και κάνε διπλό κλικ στο `Run speed test.cmd`. Αν τα Windows δείξουν
   «Windows protected your PC» (το αρχείο δεν έχει ψηφιακή υπογραφή), πάτα **More info** και μετά **Run anyway**.
4. Περίμενε μερικά λεπτά μέχρι να γράψει **Done** και στείλε πίσω το αρχείο `RESULT-....json`.

Απαιτήσεις: Windows 10 ή 11 (64-bit), περίπου 3 GB ελεύθερη μνήμη RAM, 1,5 GB χώρο στον δίσκο.
