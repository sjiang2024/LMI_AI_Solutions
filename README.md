# LMI AI Solutions
This repo contains the utils scripts, and several submodules for LMI Technologies Inc. AI modeling development.
Currently, the following submodules are included in the repo:
- [yolov5](https://github.com/lmitechnologies/yolov5)
- [efficientnet](https://github.com/lmitechnologies/EfficientNet-PyTorch)
- [tensorflow object detection API](https://github.com/lmitechnologies/models)
- [paddleOCR](https://github.com/lmitechnologies/models)
- [tf-trt](https://github.com/tensorflow/tensorrt.git)
- [tensorrtx](https://github.com/lmitechnologies/tensorrtx.git)

## Clone this master repo
For users who haven't set up the ssh keys
```bash
git clone https://github.com/lmitechnologies/LMI_AI_Solutions.git
```
For users who have the ssh keys
```bash
git clone https://github.com/lmitechnologies/LMI_AI_Solutions.git
# npm using git for https
git config --global url."git@github.com:".insteadOf https://github.com/
git config --global url."git://".insteadOf https://
```

## Clone submodules
Go to the master repo
```bash
cd LMI_AI_Solutions
```
Each submodule is pointing to a specific commit in its `ais` branch. Clone the submodules to the commit that is specified in this repo 
```bash
git submodule update --init
```
(**not recommend**) if you want to update all submodules to the `lastest` commit in the `ais` branch, use the `--remote` argument
```bash
git submodule update --init --remote
```

## Use this repo
1. Activate the environmental file - [lmi_ai.env](https://github.com/lmitechnologies/LMI_AI_Solutions/blob/ais/lmi_ai.env): 
```bash
source PATH_TO_REPO/lmi_ai.env
```
where ``PATH_TO_REPO`` is the path to the LMI_AI_Solutions repo.   

2. Run any scripts in this repo, for example:
```bash
python -m label_utils.plot_labels -h
```

## Make contributions to this repo
The `ais` branch of this repo and that branch of submodules are protected, which means you can't directly commit to that branch. You could create a new branch and open the pull request in order to merge into `ais` branch.
