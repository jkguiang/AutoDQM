if ! [[ -e new_files.json ]] ; then
    touch new_files.json
fi

python cron_dqm.py '{"cron":"/SingleMuon/Run2017*PromptReco*/DQMIO"}'
