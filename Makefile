ifndef DEPLOYMENT_NAME
$(error DEPLOYMENT_NAME is not set)
endif

include deployments/$(DEPLOYMENT_NAME).config

all:
	cp docker-compose.template.yml docker-compose.yml
	sed -i "s/REPLACE_WITH_DEPLOYMENT_NAME/$(DEPLOYMENT_NAME)/g" docker-compose.yml
	sed -i "s/REPLACE_WITH_SLACK_BOT_TOKEN/$(SLACK_TOKEN)/g" docker-compose.yml
	sed -i "s/REPLACE_WITH_MYSQL_PASSWORD/$(MYSQL_PASSWORD)/g" docker-compose.yml

	cp setup_db.template.sh setup_db.sh
	sed -i "s/REPLACE_WITH_MYSQL_PASSWORD/$(MYSQL_PASSWORD)/g" setup_db.sh
	sed -i "s/REPLACE_WITH_MYSQL_ROOT_PASSWORD/$(MYSQL_ROOT_PASSWORD)/g" setup_db.sh
	sed -i "s/REPLACE_WITH_CHANNEL_ID/$(CHANNEL_ID)/g" setup_db.sh
	sed -i "s/REPLACE_WITH_ADMIN_USER_ID/$(ADMIN_USER_ID)/g" setup_db.sh

	cp bot/config.template.py bot/config.py
	sed -i "s/REPLACE_WITH_BOT_NAME/$(BOT_NAME)/g" bot/config.py
