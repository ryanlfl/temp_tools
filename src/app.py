import dash
from dash import Output,Input,State
import base64
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import xlsxwriter
import io, time
import dash_bootstrap_components as dbc

from dash.long_callback import DiskcacheLongCallbackManager
import diskcache
from toolbox.utils.here_maps_utils import *


cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

app = dash.Dash(__name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    background_callback_manager=long_callback_manager,
)
server = app.server

app.layout = dbc.Container([
    html.H1("On Road Distance Calculator"),
    dcc.Upload(
        id="upload-excel",
        children=html.Div(id="up_data",children=["Upload Excel File"]),
        multiple=False,
        accept=".xlsx",
        style={
            "width": "30%",
            "height": "60px",
            "lineHeight": "60px",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "5px",
            "textAlign": "center",
            "margin": "10px",
            "backgroundColor": "lightblue",
        },
    ),
    dcc.Download(id="download-excel",type="application/octet-stream"),
])

@app.long_callback(
    output=[
        Output("download-excel", "data"),
        # Output("download-excel", "filename"),
    ],
    inputs=[
        Input("upload-excel", "contents"),
    ],
    running=[
        (Output("up_data","children"),[dbc.Spinner(id="common_spinner",color="primary")],["Upload Excel File"]),
    ],
    prevent_initial_call=True
)
def get_output(contents):
    if contents is not None:
        # Get the Excel file contents as a base64 encoded string
        excel_file_contents = contents.split(",")[1]

        # Decode the Excel file contents
        excel_file_bytes = base64.b64decode(excel_file_contents)

        # Create a Pandas dataframe from the Excel file contents
        df = pd.read_excel(io.BytesIO(excel_file_bytes),engine='openpyxl')
        location_list = []
        location_list_extended = []
        access_token = get_here_maps_access_token("G4eGsCcUkQVmDQaBPB6_cA","HPeYYUmNEWg17AbVxWCT7mDMGr4AkaxUttGbAgX8YqfOTv8uWpxHUGS33TWsZc_PnEnXftLXZ4Qm_fmm1tLwOA")
        for idx,row in df.iterrows():

            if pd.isnull(row.get("Latitude")) or pd.isnull(row.get("Longitude")):
                location = row.get("Location")
                latitude, longitude = geocode_location(access_token,location)
                df.loc[idx, 'Latitude'] = latitude
                df.loc[idx, 'Longitude'] = longitude

            location_list.append( { "lat": df.loc[idx, 'Latitude'], "lng": df.loc[idx, 'Longitude'] } )
            location_list_extended.append({ "loc":df.loc[idx, 'Location'],"lat": df.loc[idx, 'Latitude'], "lng": df.loc[idx, 'Longitude'] } )

        rdc = RoadDistanceCalculator()
        result = rdc.create_job(access_token,location_list)
        distances = rdc.get_job_result(access_token,result.get("status_url"))

        len_location_list_extended = len(location_list_extended)
        df_distance = pd.DataFrame(columns=['Origin', 'OriginLatitude', 'OriginLongitude','Destination','DestinationLatitude','DestinationLongitude','Distance(m)'])
        for idx_o,origin in enumerate(location_list_extended):
            for idx_d,destination in enumerate(location_list_extended):

                _ = pd.DataFrame({'Origin':[origin.get("loc")], 'OriginLatitude':[origin.get("lat")], 'OriginLongitude':[origin.get("lng")],'Destination':[destination.get("loc")],'DestinationLatitude':[destination.get("lat")],'DestinationLongitude':[destination.get("lng")],'Distance(m)':[ distances[(idx_o*len_location_list_extended)+idx_d] ]})
                df_distance = pd.concat([df_distance,_])



        # Write the Pandas dataframe to the new Excel file
        # output = io.BytesIO()
        writer = pd.ExcelWriter("output.xlsx", engine='xlsxwriter')

        df.to_excel(writer,sheet_name="geocode")
        df_distance.to_excel(writer,sheet_name="distance")
        writer.close()
        # output.seek(0)

        # Return the contents of the new Excel file
        # return (dcc.send_data_frame(df.to_excel, "output.xlsx"),)
        # excel_content = base64.b64encode(output.read()).decode("utf-8")
        with open("output.xlsx","rb") as fob:
            excel_content = base64.b64encode(fob.read()).decode("utf-8")

        # return {"content":excel_content,"filename":"o.xlsx"},
        return dcc.send_file("output.xlsx"),





if __name__ == "__main__":
    app.run_server(debug=True)
