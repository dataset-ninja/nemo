Dataset **NEMO** can be downloaded in [Supervisely format](https://developer.supervisely.com/api-references/supervisely-annotation-json-format):

 [Download](https://assets.supervisely.com/supervisely-supervisely-assets-public/teams_storage/K/6/fN/3JfKA99yu65iBjQ9TDGvJMS7uc0He4bpj3UxaEr7J03TV2gFeWvOV3oItjurxKgqfRIfukPp1OOJxDHgH9SAaZa19GYt8yNF75OyjbLK2tnaN6OH0VXJTwskW3JJ.tar)

As an alternative, it can be downloaded with *dataset-tools* package:
``` bash
pip install --upgrade dataset-tools
```

... using following python code:
``` python
import dataset_tools as dtools

dtools.download(dataset='NEMO', dst_dir='~/dataset-ninja/')
```
Make sure not to overlook the [python code example](https://developer.supervisely.com/getting-started/python-sdk-tutorials/iterate-over-a-local-project) available on the Supervisely Developer Portal. It will give you a clear idea of how to effortlessly work with the downloaded dataset.

The data in original format can be [downloaded here](https://www.kaggle.com/datasets/werus23/nevada-smoke-detection-data/download?datasetVersionNumber=1).