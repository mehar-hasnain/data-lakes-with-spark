import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format
from pyspark.sql.types import TimestampType as TimeStamp


config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID']=config.get('AWS', 'AWS_ACCESS_KEY_ID')
os.environ['AWS_SECRET_ACCESS_KEY']=config.get('AWS', 'AWS_SECRET_ACCESS_KEY')


def create_spark_session():
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
    """
    This function loads songs data from S3 and processes it by extracting the songs and artist tables
    and then save it to S3 as parquet files.
    
    Parameters:
    
        spark : Apache Spark session
        input_data : The path prefix for the song data.
        output_data : The path prefix for the output data.
    
    """
        
    # get filepath to song data file
    song_data = os.path.join(input_data, "song-data/A/A/A/*.json")
  
    
    # read song data file
    print(f'reading songs data from {song_data}')
    df = spark.read.json(song_data)

    # extract columns to create songs table
    song_columns = ['song_id', 'title', 'artist_id', 'year', 'duration']
    songs_table = df.select(*song_columns).dropDuplicates(["song_id"])
    
    # write songs table to parquet files partitioned by year and artist
    songs_table.write.partitionBy('year', 'artist_id').parquet(os.path.join(output_data, 'songs.parquet'), 'overwrite')
    print('Written songs parquet')

    # extract columns to create artists table
    artists_table = df['artist_id', 'artist_name', 'artist_location', 'artist_latitude', 'artist_longitude']
    artists_table = artists_table.dropDuplicates(['artist_id'])
    
    # write artists table to parquet files
    artists_table.write.parquet(os.path.join(output_data, 'artists.parquet'), 'overwrite')
    print('Written artists parquet')


def process_log_data(spark, input_data, output_data):
    """
    This function loads log_data from S3 and processes it by extracting the users, time and songplays tables
    and then save it to S3 as parquet files.

    Parameters:
        spark       : Spark Session
        input_data  : location of log_data json files with the events data
        output_data : S3 bucket were dimensional tables in parquet format will be stored

    """
    # get filepath to log data file
    log_data = os.path.join(input_data,"log_data/*/*/*.json")

    # read log data file
    df = spark.read.json(log_data)
    
    # filter by actions for song plays
    df = df[df['page'] == 'NextPage']

    # extract columns for users table    
    users_table = df.select(
        df.userId.alias("user_id"),
        df.firstName.alias("first_name"),
        df.lastName.alias("last_name"),
        df.gender,
        df.level).dropDuplicates(["user_id"])
    
    # write users table to parquet files
    users_table.write.parquet(os.path.join(output_data, 'users.parquet'), 'overwrite')
    print('Written users parquet')

    # create timestamp column from original timestamp column
    get_timestamp = udf(lambda x: datetime.datetime.fromtimestamp(x / 1000), TimeStamp())
    df = df.withColumn("timestamp", get_timestamp(col("ts")))
    
    # create datetime column from original timestamp column
    get_datetime = udf(lambda x: datetime.fromtimestamp(x / 1000), TimeStamp())
    df = df.withColumn("datetime", get_datetime(col("ts")))
    
    # extract columns to create time table using selectExpr
    time_table = df.selectExpr("timestamp as start_time",
                               "hour(timestamp) as hour",
                               "dayofmonth(timestamp) as day",
                               "weekofyear(timestamp) as week",
                               "month(timestamp) as month",
                               "year(timestamp) as year",
                               "dayofweek(timestamp) as weekday"
                               ).dropDuplicates(["start_time"])
    
    # write time table to parquet files partitioned by year and month
    time_table.write.partitionBy('year', 'month').parquet(os.path.join(output_data, 'time.parquet'), 'overwrite')
    print("Written time parquet")
                    

    # read in song data to use for songplays table
    song_data = os.path.join(input_data, "song-data/A/A/A/*.json")
    song_df = spark.read.json(song_data) 
                       
    song_df.createOrReplaceTempView("song_data")
    df.createOrReplaceTempView("log_data")

    # extract columns from joined song and log datasets to create songplays table 
    songplays_table = spark.sql("""
                                SELECT monotonically_increasing_id() as songplay_id,
                                ld.timestamp as start_time,
                                year(ld.timestamp) as year,
                                month(ld.timestamp) as month,
                                ld.userId as user_id,
                                ld.level as level,
                                sd.song_id as song_id,
                                sd.artist_id as artist_id,
                                ld.sessionId as session_id,
                                ld.location as location,
                                ld.userAgent as user_agent
                                FROM log_data ld
                                JOIN song_data sd
                                ON (ld.song = sd.title
                                AND ld.length = sd.duration
                                AND ld.artist = sd.artist_name)
                                """)

    # write songplays table to parquet files partitioned by year and month
    songplays_table.write.partitionBy('year', 'month').parquet(os.path.join(output_data, 'songplays.parquet'), 'overwrite')
    print("Written songplays parquet")


def main():
    spark = create_spark_session()
    input_data = "s3a://udacity-dend/"
    output_data = "s3a://mehar-hasnain/"
    
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()
