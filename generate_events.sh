for i in {1..5}; do
  echo ">>> Sending query $i"
  q="Which songs use deceptive cadences? $i?"
  conv_id=$(http POST :8000/rag question="$q" | jq -r .conversation_id)
  echo "conversation_id = $conv_id"

  # Alternate thumbs up/down feedback
  if (( i % 2 == 0 )); then
    fb=1
  else
    fb=-1
  fi

  http POST :8000/feedback conversation_id=$conv_id feedback:=$fb
  sleep 2
done