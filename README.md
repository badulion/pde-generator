# Generating equations

To generate equations randomly run 

    python main.py random [OPTIONS]

To generate equations from string run

    python main.py from_str --equation "2.654*u_x_1_y_0^1+3.123*u_x_0_y_1^1" --save-path data/out --seed 42

some equations that work nicely are:

    2.654*u_x_1_y_0^1+3.123*u_x_0_y_1^1
    2.654*u_x_1_y_0^1+3.123*u_x_0_y_1^1+0.032*u_x_2_y_0^1+0.029*u_y_0_x_2^1