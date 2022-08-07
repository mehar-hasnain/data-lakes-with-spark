# Introduction

A music streaming startup, Sparkify has grown their user base and song database
at large scale and want to move their data warehouse to a data lake. Their data
resides in S3 in a directory of JSON logs and JSON metadata of the songs.

As a data engineer, we are required to build an ETL pipeline that
extracts their data from S3, processes them using Spark, and loads the data back
into S3 as a set of dimensional tables in parquet format.

This project builds an ETL pipeline for a data lake hosted on S3. Data is loaded
from S3, processed into analytics tables using Spark, and loaded back into S3.

## Dataset

The data for this project is available on Amazon S3.

- Song data: s3://udacity-dend/song_data
- Log data: s3://udacity-dend/log_data

### Log Data

The JSON logs on user activity have the following structure.

![log data](log-data.png)

### Song Data

Below is an example of what a single song file, TRAABJL12903CDCF1A.json looks
like.

```JSON
{"num_songs": 1, "artist_id": "ARJIE2Y1187B994AB7", "artist_latitude": null,
"artist_longitude": null, "artist_location": "", "artist_name": "Line Renaud",
"song_id": "SOUPIRU12A6D4FA1E1", "title": "Der Kleine Dompfaff",
"duration": 152.92036, "year": 0}
```

### Configuration

Add following information in config file `dl.cfg`. IAM user must have read and write permissions to S3. If output bucket is not already there create one.

```cfg
[AWS]
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
```

### Run  project

run the ETL script.

```bash
python etl.py
```

On each stage messages are printed in the shell.