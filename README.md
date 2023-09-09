# automatic_dataset_conversion
This repository is a complement to EDVO: End-To-End Learned VO with Event Cameras for Moon Landing 
for automatic dataset conversion and managing.

## Example: convert TartanAir
1. First activate edvo environment as report in [EDVO](https://github.com/uzh-rpg/master_thesis_roberto_pellerito):
2. Install on edvo env [VID2E](https://github.com/uzh-rpg/rpg_vid2e) and [EV-LICIOUS](https://github.com/uzh-rpg/ev-licious)
3. specify your dataset path in [generate_events.sh](https://github.com/senecobis/automatic_dataset_conversion/blob/master/other_scripts/generate_events.sh)
4. run """shell
          bash generate_events.sh
           """
5. After the process ends, convert your dataset with [generate_events.sh](https://github.com/senecobis/automatic_dataset_conversion/blob/master/other_scripts/convert_events.sh)
6. Check your dataset with [check_dataset.sh](https://github.com/senecobis/automatic_dataset_conversion/blob/master/other_scripts/check_dataset.sh)
