# Model notice

`data/greek-ctc.onnx` is the model
[jonatasgrosman/wav2vec2-large-xlsr-53-greek](https://huggingface.co/jonatasgrosman/wav2vec2-large-xlsr-53-greek)
by Jonatas Grosman, licensed under the Apache License 2.0 (see `Apache-2.0.txt`).
It is a fine-tune of [facebook/wav2vec2-large-xlsr-53](https://huggingface.co/facebook/wav2vec2-large-xlsr-53)
(Apache License 2.0) on Common Voice 6.1 and CSS10.

Change made for this test: the original PyTorch weights were converted, unchanged and at
full 32-bit precision, to the ONNX format so that ONNX Runtime can run them. No retraining.

Citation requested by the model author:

    @misc{grosman2021xlsr53-large-greek,
      title={Fine-tuned {XLSR}-53 large model for speech recognition in {G}reek},
      author={Grosman, Jonatas},
      howpublished={\url{https://huggingface.co/jonatasgrosman/wav2vec2-large-xlsr-53-greek}},
      year={2021}
    }

The test sounds are synthetic: `gpu_bench.py` generates them from fixed numbers at run time.
No recordings are included.
