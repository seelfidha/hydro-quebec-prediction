Configure postgres via docker 
    create a new server
        specify the server name 
        next tab "connexion" specify the container ip address (check next sections for command lines)
        db name defined in docker compose 
        admin and password 

get container ip address 
    check the list of containers using: "docker container ls"
    for a specific container execute docker "inspect 'container_id'"

Once connected, the database tables will be automatically created and the data will be injected 
This is under the test_db database, two main tables will be present : 
processed_ids & pannes 
here are some sql queries to check the data injected: 
select count(*) from pannes 
select count(*) from processed_ids
select * from pannes
select callid_processed, count(id) from pannes group by callid_processed

to export data from postgres container instance: 
open terminal inside 'database' project folder and execute the following command: 
docker exec postgres_db pg_dump -U root -d test_db > backup.sql
