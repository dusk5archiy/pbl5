. scripts/venv.sh

if [[ ! -f "output/dice-score-model.pth" ]]; then
  python model/dice_score_model_train.py
fi

if [[ ! -f "output/dice-pos-model.pth" ]]; then
  cat >"yolo-data/data.yaml" <<EOF
path: yolo-data
train: images/train
val: images/val

nc: 1
names: ['dice']
EOF
  python model/dice_pos_model_train.py

  if [[ -f "yolo-output/train/weights/best.pt" ]]; then
    cp yolo-output/train/weights/best.pt output/dice-pos-model.pt
  fi
fi

rm -r yolo11n.pt
