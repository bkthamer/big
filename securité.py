pip install pandas==1.5.3
 
tekteb crontab -e
tokhrej interface tahbet loutaaaa w tekteb cron mteeik ly howa hedha 
*/2 * * * * /opt/spark/spark-3.5.3-bin-hadoop3/bin/spark-submit /home/thamer/Bureau/examen/dataexterne.py
 
cntrl o contrl x bech tenregistri mbaed c'est bon ywali yekhdem 
 
 
which spark-submit yaatini win howa w nestaamloha bel cron
 dd
 
built in function 
 
col() – Référencer une colonne.
lit() – Ajouter une valeur fixe comme colonne.
when() / otherwise() – Conditions simples (type IF-ELSE).
trim() – Supprimer les espaces d'une chaîne.
lower() / upper() – Convertir en minuscules/majuscules.
count() – Compter les lignes ou les valeurs dans un groupe.
avg() – Calculer la moyenne d'une colonne numérique.
sum() – Calculer la somme d'une colonne numérique.
distinct() – Supprimer les doublons.
orderBy() – Trier les données (ascendant ou descendant).
isnull() / isnotnull() – Vérifier les valeurs nulles ou non nulles.
substring() – Extraire une partie d’une chaîne.
split() – Diviser une chaîne en fonction d'un séparateur.
concat() – Combiner plusieurs colonnes ou valeurs.
round() – Arrondir une valeur numérique.
 
 
lezem tasnaa dossier haka hdfs dfs -mkdir -p /projet
w mbaaed taaty droit bech tnajem tekteb fih hdfs dfs -chmod -R 777 /projet
 
 
 
****************************************************************************
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, when
from pyspark.sql import functions as F
 
 
spark = SparkSession.builder \
    .appName("loc") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.sql.dynamicAllocation.enabled", "true") \
    .config("spark.sql.dynamicAllocation.minExecutors", "2") \
    .config("spark.sql.dynamicAllocation.maxExecutors", "10") \
    .getOrCreate()
 
url_lire = "hdfs://localhost:9000/share/openfood1.csv"
 
 
df = spark.read.csv(url_lire, header=True, inferSchema=True)
 
 
 
 
 
col_to_check = ["code", "categories"]  
 
 
df_cleaned = df.na.drop(subset=col_to_check)
 
 
df_cleaned = df_cleaned.dropDuplicates(["code"])
 
 
nbr1 = df_cleaned.count()
 
 
df_cleaned = df_cleaned.fillna({"brands": "unknown"})
 
 
df_cleaned = df_cleaned.withColumn("categories", trim(col("categories")))
 
 
df_cleaned = df_cleaned.withColumn(
    "brands",
    when(col("brands").isin("YAMI", "thamer"), "thamer")
    .when(col("brands").isin("Mission", "boukhris"), "boukhris")
    .otherwise(col("brands"))
)
 
df_cleaned.createOrReplaceTempView("table")
 
 
 
 
print("**************")
print(f"Nombre initial : {df.count()}")
print(f"Nombre après nettoyage : {nbr1}")
 
spark.sql("select brands , code from table where brands == 'thamer' ").show()
 
df_cleaned.printSchema()
 
spark.sql("select stores ,code ,sum(serving_quantity) as somme from table group by stores,code").show()
 
df_ordrerd = df_cleaned.orderBy("code")
 
df_ordrerd.createOrReplaceTempView("table1")
spark.sql("select code from table1").show()
 
df_grouped = df_cleaned.groupBy("code").agg(F.avg("serving_quantity").alias("somme"))
 
df1 = df_cleaned.select(col("code"))
df2 = df_cleaned.filter(df_cleaned["brands"] == "boukhris")
 
df2.createOrReplaceTempView("t")
spark.sql("select brands , code from t").show()
 
df2.write.mode("overwrite").parquet("hdfs://localhost:9000/share/h.parquet")
df2.write.mode("overwrite").csv("hdfs://localhost:9000/share/h1.csv")
 
thamer = spark.read.parquet("hdfs://localhost:9000/share/h.parquet",header=True)
thamer.printSchema()
 
 
schema_ddl = """
    code BIGINT,
    url STRING,
    last_updated_t INT,
    serving_quantity DOUBLE
"""
 
df_ddl = spark.read.csv("hdfs://localhost:9000/share/h1.csv",schema=schema_ddl)
 
df_ddl.printSchema()
df_ddl.show()
 
****************************************************************************
 
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
 
 
spark = SparkSession.builder \
    .appName("combine") \
    .config("spark.sql.shuffle.partitions", "200") \
    .getOrCreate()
 
 
url_loc = "hdfs://localhost:9000/projet/data_loc.csv"
url_dyn = "hdfs://localhost:9000/projet/datadynamique.csv"
 
 
df = spark.read.csv(url_loc, header=True, inferSchema=True)
df1 = spark.read.csv(url_dyn, header=True, inferSchema=True)
 
 
df = df.withColumnRenamed("Population", "Population_loc") \
       .withColumnRenamed("Region", "Region_loc")
 
df1 = df1.withColumnRenamed("population", "Population_dyn") \
         .withColumnRenamed("region", "Region_dyn") \
         .withColumnRenamed("name", "Country")
 
 
df = df.withColumn("Country", F.lower(F.col("Country")))
df1 = df1.withColumn("Country", F.lower(F.col("Country")))
 
 
combined_df = df.join(df1, on="Country", how="inner")
 
 
print("\nSchéma du DataFrame combiné:")
combined_df.printSchema()
 
 
print("\nQuelques lignes du DataFrame combiné:")
combined_df.show(truncate=False)
 
 
output_path = "hdfs://localhost:9000/projet/combined_data123.csv"
combined_df.write.csv(output_path, header=True, mode="overwrite")
 
 
spark.stop()
 
****************************************************************************
 
from pyspark.sql import SparkSession
import pandas as pd 
import requests
from pyspark.sql.types import StructType,StructField,StringType
 
url = "https://restcountries.com/v2/all"
 
spark = SparkSession.builder \
    .appName("data_dynam") \
    .config("spark.sql.shuffle.partitions","200") \
    .config("spark.sql.dynamicAllocation.enabled","true") \
    .config("spark.sql.dynamicAllocation.minExecutors","2") \
    .config("spark.sql.dynamicAllocation.maxExecutors","10") \
    .getOrCreate()
 
 
response = requests.get(url,stream=True)
 
if response.status_code == 200 : 
    data = response.json()
else : 
    raise Exception(f"erreur {response.status_code}")
 
 
df = pd.json_normalize(data)
 
for column in df.columns :
    if isinstance(df[column].iloc[0],(list,dict)):
        df[column]=df[column].astype(str)
 
 
schema1 = StructType([StructField(col,StringType(),True) for col in df.columns])
 
df_created = spark.createDataFrame(df,schema=schema1)
 
df_created.printSchema()
 
urlhdfs="hdfs://localhost:9000/projet/datadynamique.csv"
 
df_created.write.mode("overwrite").csv(urlhdfs,header=True)
 
spark.stop()
 
****************************************************************************
 
from pyspark.sql import SparkSession
from pyspark.sql.functions import desc , col
spark = SparkSession.builder \
    .appName("ggg") \
    .getOrCreate()
 
 
url = "/home/thamer/players_19.csv"
df = spark.read.csv(url,header=True,inferSchema=True)
 
df.createOrReplaceTempView("table")
 
spark.sql("select position , count(*) from (select explode(split(player_positions,',')) as position , wage_eur from table) group by position").show()
 
spark.sql("select weight_kg , count(*) as num , avg(weight_kg) over (partition by position) as avg_weight , position from (select weight_kg , explode(split(player_positions,',')) as position from table) group by weight_kg,position").show()
 
#jointure
#spark.sql("select p22.short_name , p22.overall as over22 , p15.overall as over15 from players22 p22 join players15 p15 on p22.sofifa_id = p15.sofifa_id")
 
spark.sql("SELECT short_name, potential, overall FROM table").where("potential = 94").show()
 
 
spark.sql("select short_name , potential , overall from table where short_name = 'L. Messi' ").show()
 
 
spark.sql("select nationality_name , avg(overall) as avg_score from table group by nationality_name").orderBy(desc("avg_score")).show()
 
 
spark.sql("select short_name , potential , overall from table").select(col("short_name"),col("overall"),(col("potential") / col("overall"))).show()
spark.stop()
 
****************************************************************************
 
import os
import subprocess
 
script1 = "/home/thamer/Bureau/rev/comp2.py"
script2 = "/home/thamer/Bureau/rev/comp1.py"
 
def execute_func(script):
    """
    Execute the given Spark script.
    """
    print(f"Starting execution of {script}")
    try:
        subprocess.run(["/opt/spark/spark-3.5.3-bin-hadoop3/bin/spark-submit", script], check=True)
        print(f"Finished execution of {script}")
    except subprocess.CalledProcessError as e:
        print(f"Error while executing {script}: {e}")
 
if __name__ == "__main__":
    execute_func(script1)
    execute_func(script2)
 
****************************************************************************
from pyspark.sql import SparkSession
from pyspark.sql import functions as F 
 
 
spark = SparkSession.builder \
    .appName("hhh") \
    .config("spark.sql.suffle.partitions","200") \
    .config("spark.sql.dynamicAllocation.enabled","true") \
    .config("spark.sql.dynamicAllocation.minExecutors","2") \
    .config("spark.sql.dynamicAllocation.maxExecutors","10") \
    .getOrCreate()
 
 
url = "/home/thamer/Téléchargements/partie2.csv"
 
df = spark.read.csv(url,header=True,inferSchema=True)
 
 
df.printSchema()
nbr = df.count()
print(f"nbr {nbr}")
 
df_orderd = df.orderBy("age")
 
df_orderd.show()
 
df_filtred = df.filter(df["age"]>49)
 
df_filtred.show()
 
df_group = df.groupBy("city").agg(F.avg("age").alias("moyenne"))
df_group.show()
 
df.createOrReplaceTempView("table")
 
spark.sql("select * from table").show()
 
spark.sql("select age from table where city = 'Chicago'").show()
 
spark.sql("select city  , avg(age) over (partition by city) as tesss from table").show()
 
spark.stop()
 
****************************************************************************
 
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import requests
import pandas as pd 
from pyspark.sql.types import StructType,StructField,StringType
import wget
url = "https://world.openfoodfacts.org/api/v2/product/737628064502.json"
 
 
spark = SparkSession.builder \
    .appName("locloc") \
    .config("spark.sql.shuffle.partitions","200") \
    .config("spark.sql.dynamicAllocation.enabled","true") \
    .config("spark.sql.dynamicAllocation.minExecutors","2") \
    .config("spark.sql.dynamicAllocation.maxExecutors","10") \
    .getOrCreate()
 
response = requests.get(url,stream=True)
 
if response.status_code == 200:
    data = response.json()
else :
    print(f"{response.status_code}")
 
df = pd.json_normalize(data)
 
for column in df.columns :
    if isinstance(df[column].iloc[0],(list,dict)):
        df[column] = df[column].astype(str)
 
 
schema = StructType([StructField(col, StringType(), True) for col in df.columns])
 
 
 
df_cleaned = spark.createDataFrame(df,schema=schema)
 
 
df_cleaned.printSchema()
 
df_cleaned = df_cleaned.coalesce(1)
#df_cleaned.write.mode("overwrite").csv("/home/thamer/Bureau/ec/ec12.csv",header=True)
 
df_cleaned.createOrReplaceTempView("table")
 
spark.sql("select code , status , explode(split(`product._keywords`,',')) as pp from table").show()
 
spark.sql("select status , code , sum(status) over(partition by `product._keywords`) as sm  from table").show()
 
af = spark.sql("select `product.image_front_thumb_url` from table")
af.show()
 
urls = [row["product.image_front_thumb_url"] for row in af.collect()]
 
for val in  urls:
    loc = wget.download(val)
    print("******************************************")
    print("******************************************")
    print("******************************************")
    print(loc)
    print("******************************************")
    print("******************************************")
    print("******************************************")
 
 
 
spark.stop()
 
****************************************************************************
 
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, lower, regexp_replace, when, lit
from pyspark.sql.types import IntegerType, DoubleType
from datetime import datetime
 
 
def create_spark_session():
    """Crée une session Spark avec une configuration optimisée."""
    return SparkSession.builder \
        .appName("Data Cleaning and Validation Job") \
        .config("spark.sql.shuffle.partitions", "200") \
        .config("spark.sql.dynamicAllocation.enabled", "true") \
        .config("spark.sql.dynamicAllocation.minExecutors", "2") \
        .config("spark.sql.dynamicAllocation.maxExecutors", "10") \
        .getOrCreate()
 
 
def read_csv_data(spark, file_path):
    """Lit un fichier CSV et retourne un DataFrame."""
    return spark.read.csv(file_path, header=True, inferSchema=True)
 
 
def clean_and_normalize_data(df):
    """
    Nettoie et normalise les données :
    - Suppression des lignes avec valeurs nulles
    - Suppression des doublons
    - Conversion des types
    - Normalisation des colonnes (Country, Region)
    """
    required_columns = ['`Country`', '`Region`', '`Population`', '`Pop. Density (per sq. mi.)`', '`Area (sq. mi.)`', '`Net migration`', '`Literacy (%)`']
 
 
    df_cleaned = df.na.drop(subset=required_columns).dropDuplicates()
 
 
    df_cleaned = df_cleaned \
        .withColumn("Population", col("Population").cast(IntegerType())) \
        .withColumn("`Pop. Density (per sq. mi.)`", col("`Pop. Density (per sq. mi.)`").cast(IntegerType())) \
        .withColumn("`Net migration`", col("`Net migration`").cast(DoubleType()))
 
 
    df_cleaned = df_cleaned \
        .withColumn("Country", trim(lower(col("`Country`")))) \
        .withColumn("Region", trim(lower(col("`Region`")))) \
        .withColumn("Country", regexp_replace(col("Country"), "[^a-zA-Z0-9 ]", ""))
 
    return df_cleaned
 
 
def normalize_country_names(df):
    """
    Normalise les noms des pays selon un dictionnaire défini.
    Retourne un DataFrame avec une colonne 'Country_Normalized'.
    """
    normalization_dict = {
        "usa": "United States",
        "u.s.a": "United States",
        "united states of america": "United States",
        "uk": "United Kingdom",
        "england": "United Kingdom",
        "emirates": "United Arab Emirates"
    }
 
 
    df = df.withColumn(
        "Country_Normalized",
        when(col("Country").isin(*normalization_dict.keys()), lit(None)).otherwise(col("Country"))
    )
 
 
    for key, value in normalization_dict.items():
        df = df.withColumn(
            "Country_Normalized",
            when(col("Country") == key, lit(value)).otherwise(col("Country_Normalized"))
        )
 
    return df
 
 
def write_cleaned_data(df, base_path):
    """
    Écrit les données nettoyées dans un Data Lake organisé :
    - Par convention de nommage
    - Organisation par date
    """
    today_date = datetime.now().strftime("%Y-%m-%d")
    output_path = f"hdfs://localhost:9000/projet/data_loc_net.csv{today_date}"
    df.write.mode("overwrite").option("header", "true").csv(output_path)
    return output_path
 
 
def main():
 
    input_file_path = "hdfs://localhost:9000/projet/data_loc.csv"
    data_lake_path = "hdfs://localhost:9000/projet/data_loc_net.csv"
 
 
    spark = create_spark_session()
 
    try:
 
        raw_data = read_csv_data(spark, input_file_path)
        initial_count = raw_data.count()
 
 
        cleaned_data = clean_and_normalize_data(raw_data)
 
 
        normalized_data = normalize_country_names(cleaned_data)
 
 
        cleaned_count = normalized_data.count()
 
 
        output_path = write_cleaned_data(normalized_data, data_lake_path)
 
 
        print(f"Nombre de lignes dans le fichier initial : {initial_count}")
        print(f"Nombre de lignes après nettoyage : {cleaned_count}")
        print(f"Données nettoyées et enregistrées dans : {output_path}")
        cleaned_data.printSchema()
 
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
    finally:
        spark.stop()
 
 
if __name__ == "__main__":
    main()
****************************************************************************
 
 
 



