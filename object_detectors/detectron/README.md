# Training Steps

## Install the library
### Clone the LMI_AI_SOLUTIONS repository.
```bash
git clone --recursive https://github.com/lmitechnologies/LMI_AI_Solutions.git
```
### Install the Detectron2
The instructions are here: https://detectron2.readthedocs.io/en/latest/tutorials/install.html


## Create a yaml file for training

```yaml
DATASETS:
  #training dataset name(s)
  TRAIN: ("dataset_train",)
  #training dataset location(s)
  TRAIN_DIR: ("./data/2022-11-18_640_192_all",)
  TEST: ()
INPUT: 
  FORMAT: "RGB"
  MIN_SIZE_TRAIN: (640,)
  MAX_SIZE_TRAIN: 640
  RANDOM_FLIP: "horizontal"
MODEL:
  WEIGHTS: './pretrained-models/model_final_9243eb.pkl'
  BACKBONE:
    #training the whole model 
    FREEZE_AT: 0
  ROI_HEADS:
    NUM_CLASSES: 2
    BATCH_SIZE_PER_IMAGE: 128
  RESNETS:
    DEPTH: 50
    STRIDE_IN_1X1: True  # True for R50, R101; False for others
    RES2_OUT_CHANNELS: 256 # 64 for R18, R34; 256 for others
  PIXEL_MEAN: [123.675, 116.280, 103.530]
  PIXEL_STD: [58.395, 57.120, 57.375]
SOLVER:
  IMS_PER_BATCH: 8
  BASE_LR: 0.001
  #BASE_LR_END: 0.00025
  MAX_ITER: 80000
  STEPS: (60000,)
  CHECKPOINT_PERIOD: 10000
OUTPUT_DIR: './trained-inference-models/2022-11-18_R50'
VERSION: 2
```


## (optional) Download the pre-trained MaskRCNN models

```bash
The models can be found below:
  R18: https://download.pytorch.org/models/resnet18-f37072fd.pth
  R34: https://download.pytorch.org/models/resnet34-b627a593.pth
  R50: https://dl.fbaipublicfiles.com/detectron2/COCO-InstanceSegmentation/mask_rcnn_R_50_C4_1x/137259246/model_final_9243eb.pkl
  R101: https://dl.fbaipublicfiles.com/detectron2/COCO-InstanceSegmentation/mask_rcnn_R_101_C4_3x/138363239/model_final_a2914c.pkl

# for example
wget https://download.pytorch.org/models/resnet18-f37072fd.pth -P ./pretrained-models
```

## Train the model

```bash
# activate LMI_AI environment
source [REPO_PATH]/LMI_AI_Solutions/lmi_ai.env 

# train 
python -m detectron.train --input INPUT_YAML_FILE
```
where the `REPO_PATH` is the path to LMI_AI_Solutions repository, `INPUT_YAML_FILE` is the config yaml file for training.

# Testing

## Create a yaml file for testing
```yaml
DATASETS:
  # dataset name, generate subfolder inside OUTPUT_DIR
  TEST: ("2022-07-05_R18",)
  TEST_DIR: ("./data/test_512x512",)
INPUT: 
  FORMAT: "RGB"
  #set to zero to disable image resizing during testing
  MIN_SIZE_TEST: 256
  MAX_SIZE_TEST: 256
MODEL:
  ROI_HEADS:
    NUM_CLASSES: 2
    SCORE_THRESH_TEST: 0.7
  RESNETS:
    DEPTH: 18
    STRIDE_IN_1X1: False
    RES2_OUT_CHANNELS: 64
  PIXEL_MEAN: [0, 0, 0]
  PIXEL_STD: [1, 1, 1]
TRAINED_MODEL_DIR: './trained-inference-models/2022-07-05_R18'
OUTPUT_DIR: './validation'
VERSION: 2
```

## Run inference

```bash
# activate LMI_AI environment
source [REPO_PATH]/LMI_AI_Solutions/lmi_ai.env 

# test
python -m detectron.test --input INPUT_YAML_FILE
```
where the `REPO_PATH` is the path to LMI_AI_Solutions repository, `INPUT_YAML_FILE` is the config yaml file for testing.
