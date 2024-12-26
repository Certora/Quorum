.PHONY: update-version
update-version:
	python3 -c "from datetime import datetime; print(datetime.now().strftime('%Y%m%d.%H%M%S.%f'))" > version
	git add version