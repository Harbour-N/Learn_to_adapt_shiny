import matplotlib.pyplot as plt
import numpy as np
from faicons import icon_svg
from functions import *
from Params import *


from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.h1("Learning to adapt - beating cancer at its own game"),
    ui.layout_sidebar(
        ui.sidebar("Parameters",        
                   ui.input_select(  
                                    "select",  
                                    "Select treatment schedule",  
                                    {"1A": "Custom", "1B": "Continuous", "1C": "AT50", "1D": "AI agent"},  
                                ),  
                    ui.input_select(  
                                    "param_select",  
                                    "Select Parameter values",  
                                    {"PatA": "Patient A", "PatB": "Patient B"},  
                                ), 
                    ui.input_select(  
                                    "Freq_select",  
                                    "Select frequency of treatment decision",  
                                    {30: "Monthly (30 days)", 14: "Biweekly", 7: "Weekly"},  
                                ), 
                    ui.input_radio_buttons("Show", "Show sensitive and resistant populations", {0: "No", 1: "Yes"}),
        bg="#f8f8f8"), 
        "Simulation",
        ui.div(ui.input_action_button("start_stop", "Start simulation", icon=icon_svg("play"), class_="btn-success")),
        ui.output_ui("next_step_button"),  # Dynamically rendered button
        ui.input_radio_buttons(  
        "radio",  
        "Treatment on or off",  
        {0: "Off (D = 0)", 1: "On (D = 1)"}),
        ui.output_ui("AT50_recommendation"),
        ui.output_ui("Tumor_size"),
        ui.output_plot("plot"),

    )
)


def server(input: Inputs, output: Outputs, session: Session):

    # Store simulation state
    running = reactive.Value(False) # Keep track of if the simulation is running
    proceed_counter = reactive.Value(0) # Keep track of the number of times the next step button has been clicked
    time = reactive.Value(0) # keep track of the time step - this is updated everytime the next step button is clicked
    # Initialize reactive lists to store results
    sol_save = reactive.Value([])  # Stores tumor sizes
    time_save = reactive.Value([])  # Stores time points
    s_save = reactive.Value([])  # Stores s values
    r_save = reactive.Value([])  # Stores r values

    # Params reactively change
    params = reactive.Value([0.027, 1,0.0,0.0,1.5,1,0.74,0.01])

    max_time = 1100
    t = np.arange(0, max_time, 1)
    lw = 3

    @reactive.effect
    @reactive.event(input.start_stop)
    def toggle_simulation():
        """Toggles the simulation on/off and resets the timestep."""
        running.set(not running.get())  # Toggle the simulation state
        if running.get():
            time.set(0) # reset the timestep when starting the simulation
            ui.update_action_button("start_stop", label="Stop simulation", icon=icon_svg("stop"))
            sol_save.set([])
            time_save.set([])
            s_save.set([])
            r_save.set([])

        else:
            ui.update_action_button("start_stop", label="Start simulation", icon=icon_svg("play"))
            proceed_counter.set(0)

    @render.ui
    def next_step_button():
        """Render the 'Proceed to Next Step' button only when the simulation is running."""
        if running.get():
            return ui.input_action_button("next_step", "Proceed to Next Step", class_="btn-primary")
        return None  
    
    # Update the model parameter based on the selected patient
    @reactive.effect
    @reactive.event(input.param_select)
    def params_reactive():
        if input.param_select() == "PatA":
            # [r_s, r_R_scale,d_s,d_R,d_D,k,s0,r0]
            rs = 0.035
            params.set([rs,0.54,0.001*rs,0.001*rs,1.5,1,0.74,0.01])
        elif input.param_select() == "PatB":
            params.set([0.027, 0.75,0.01,0.012,1.5,1,0.74,0.01])
    


    @reactive.effect
    @reactive.event(input.next_step)
    def next_step():

        if time.get() < max_time:
            new_time = time.get() + int(input.Freq_select())
            time_ = np.arange(time.get(), new_time+1, 1)

            time.set(new_time)
            proceed_counter.set(proceed_counter.get() + 1)

            # Solve LV model
            D = int(input.radio())
            current_params = list(params.get())
            if not sol_save.get():
                IC = current_params[6:8]
            else:
                IC = [s_save.get()[-1], r_save.get()[-1]]
            
            current_params[6:8] = IC
            
            sol = LV_model(time_,current_params,D)
            N = sol[0, :] + sol[1, :]

            # Append new results
            s_save.set(s_save.get() + list(sol[0, :]))
            r_save.set(r_save.get() + list(sol[1, :]))
            sol_save.set(sol_save.get() + list(N))
            time_save.set(time_save.get() + list(time_))
        else:
            running.set(False)
            ui.update_action_button("start_stop", label="Start simulation", icon=icon_svg("play"))
            proceed_counter.set(0)

    @render.plot
    def plot():
        fig, ax = plt.subplots()
        ax.set_xlabel("Time")
        ax.set_ylabel("Relative PSA level (tumor burden)")
        ax.set_ylim(0, 1.25)
        ax.set_xlim(0, max_time)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1, 1.2])
        ax.set_yticklabels(['0%','25%', '50%','75%','100%','120%'])

        ax.hlines(1.2, 0, max_time, color = 'blue' ,linestyles='dashed', label='Tumor size limit',linewidth = lw)

        current_params = list(params.get())
        show = int(input.Show())

        # Plot stored data as relative tumor size
        if sol_save.get() and time_save.get():
            ax.plot(time_save.get(), sol_save.get() / np.sum(current_params[6:8]),markersize = 0.5, label="Total tumor size",color = 'black', linewidth = lw)
            if show == 1:
                ax.plot(time_save.get(), s_save.get() / np.sum(current_params[6:8]),'--',markersize = 0.5, label="Sensitive tumor size",color = 'green', linewidth = lw)
                ax.plot(time_save.get(), r_save.get() / np.sum(current_params[6:8]),'--',markersize = 0.5, label="Resistant tumor size",color = 'red',linewidth = lw)
        
        return fig
    
    
    @render.ui
    def AT50_recommendation():
        """Render AT50 recommendation only when AT50 is selected."""
        if input.select() == "1C":
            string = "AT50 Rule: Treat tumour until it has reduced to 0.5 of its original size. Then stop treatment until it returns to its original size (Repeat)."

            return ui.p(string, style="color: #2c3e50; font-weight: bold;")
        else:
            return None
    
    @render.ui
    def Tumor_size():
        """Render Tumor size to help"""
        if input.select() == "1C":
            current_params = list(params.get())
            if sol_save.get():
                size = sol_save.get()[-1] / np.sum(current_params[6:8])
                string = f"Tumor size: {size:.3f}"
            else:
                size = 1
                string = f"Tumor size: {size:.3f}"
            
            return ui.p(string, style="color: #2c3e50; font-weight: bold;")
        return None

    

    







app = App(app_ui, server)
