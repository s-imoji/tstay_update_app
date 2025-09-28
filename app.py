from flask import Flask, render_template, request
from google.cloud import bigquery
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

app = Flask(__name__)

@app.route('/')
def bigquery_query():
    """
    This function connects to BigQuery, runs a query, and renders the results in an HTML template.
    """
    try:
        # Create a BigQuery client
        client = bigquery.Client()

        # Get the 'delta' value from the request arguments, default to 1 if not provided.
        delta = request.args.get('delta', default=1, type=int)

        # Define your query
        # The user mentioned get_query, but based on the code, query_string is the correct function.
        query = query_string(delta=delta)

        # Run the query
        query_job = client.query(query)

        # Get the results
        results = query_job.result()

        return render_template('index.html', results=results, delta=delta)

    except Exception as e:
        return f"An error occurred: {e}"

def get_yesterday_string(delta = 1 ):
    tokyo_tz = ZoneInfo("Asia/Tokyo")
    yesterday = datetime.now(tokyo_tz) - timedelta(days=delta)
    return yesterday.strftime('%Y-%m-%d')

def query_string(delta = 1 ):

        # Get yesterday's date string to use in the query
        yesterday_str = get_yesterday_string(delta=delta)
        timestamp_str = f"{yesterday_str} 09:00:00"

        query = f"""
            select  
        
                    if(
                        timestamp_seconds(mmm_resv.created_at) >=  timestamp('{timestamp_str}', 'Asia/Tokyo'),"0_新規","1_更新"
                    ) as create_flg,
                    mmm_building.building_name,
                    --mmm_resv.created_at,
                    --mmm_resv.updated_at,
                    
                    format_timestamp('%Y-%m-%d %H:%M:%S', 
                    timestamp_seconds(mmm_resv.created_at),
                                    'Asia/Tokyo'  
                    ) as create_string_timestamp,

                    format_timestamp('%Y-%m-%d %H:%M:%S', 
                    timestamp_seconds(mmm_resv.updated_at),
                                    'Asia/Tokyo'  
                    ) as update_string_timestamp,
                    
                    timestamp_seconds(mmm_resv.created_at) as create_timestamp,

                    timestamp_seconds(mmm_resv.updated_at) as update_timestamp,

                    mmm_listing.name as room_name,
                    mmm_resv.ota_type,
                    mmm_resv.id_on_ota as reservation_no,
                    mmm_resv.start_date,
                    mmm_resv.end_date,
                    mmm_resv.accepted,
                    if(
                        mmm_resv.cancelled_at > 0,

                        format_timestamp('%Y-%m-%d %H:%M:%S', 
                            timestamp_seconds(mmm_resv.cancelled_at),
                                    'Asia/Tokyo'  
                        ),null
                    ) as cancel_string_timestamp,

                    

            from    `m2m-core.m2m_core_prod.reservation` mmm_resv
            left outer join
                    `m2m-core.m2m_core_prod.listing` mmm_listing
            on
                    mmm_resv.listing_id = mmm_listing.id
            left outer join
                    `m2m-core.dx_001_room.room_id` mmm_room_id
            on
                    mmm_listing.id = mmm_room_id.room_id
            left outer join
                    `m2m-core.dx_003_building.building_name` mmm_building
            on
                    mmm_room_id.building_id = mmm_building.building_id
            where
                    mmm_listing.name like '%東急ステイ%'
            and     
                    timestamp_seconds(mmm_resv.updated_at) >=  timestamp('{timestamp_str}', 'Asia/Tokyo')
            order by  
                    if(
                        timestamp_seconds(mmm_resv.created_at) >=  timestamp('{timestamp_str}', 'Asia/Tokyo'),"0_新規","1_更新"
                    ),
                    mmm_building.building_name,
                    mmm_resv.updated_at
        """
        return query

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
