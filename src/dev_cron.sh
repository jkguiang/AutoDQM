if ! [[ -e /nfs-6/userdata/AutoDQM/fmap.json ]] ; then
    touch /nfs-6/userdata/${USER}/AutoDQM/fmap.json
fi

python dev_cron.py '{"cron":"/SingleMuon/Run2017*PromptReco*/DQMIO"}'
