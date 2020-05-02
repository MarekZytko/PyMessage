if [ `id -u` -ne 0 ]; then
	echo "This script can be executed only as root, Exiting.."
	exit 1
fi

echo "This script will update repo constantly and will periodically restart server"

read -p "Do you want to add 'cronjob.sh' script to crontab? [y/n]" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
	echo "adding path to crontab..."
	echo "PATH=/bin:/usr/bin:/home/centos/pymessage" | crontab -
	
	echo "adding $(echo $PWD/cronjob.sh) to crontab..."
	(crontab -l && echo "*/5 * * * * cd $PWD/cronjob.sh; bash -l -c cronjob.sh") | crontab -
	echo "job added to crontab!"
fi
