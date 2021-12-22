# Dash-based dashboards

Explore the predictive capabilities and limitations of linear approximate models on portions of Mauna Loa CO2.
Dashboard originally developed for ENVR 300 at UBC. 

## How to run locally (on your own computer)
Dash is a library for making interactive applications that will run in a browser window. See https://dash.plotly.com/. We are using "Dash open-source" NOT Dash Enterprise. 

The graphics in our dashboards are produced using the plotly library. See https://plotly.com/python/

Python code is in the *.py files. They are commented - see top few lines for how to run them. These are NOT developed or run in Jupyter notebooks. That will come soon, but for now, the workflow and debugging is very efficient without notebooks.

The dash packages do need installing via `pip install dash==1.18.1` (see [Dash installation](https://dash.plotly.com/installation)). 

After installing, the necessary packages for running the codes are in the conda mini "base" environment. That means development can simply involve editing in a text editor and running with debugging on - achieved by including these as the last 2 lines of your code:
```
if __name__ == '__main__':
    app.run_server(debug=True)
```

Run the app from your terminal (in the directory with the *.py file) with `python app3.py`, then visit http://127.0.0.1:8050/ in your web browser. 

End by closing the browser window and typing CTRL-C in your terminal. 