# OpenWebUI + Agent-S Setup (Kid-Friendly Guide)

These steps show a young helper how to turn on OpenWebUI so it can talk to Agent-S (the robot that looks at the screen and helps). Follow each step in order and ask an adult if something looks different.

## What you need first
- A terminal window (press `Ctrl` + `Alt` + `T` on Linux).
- This project already downloaded in `/home/stacy/AlphaOmega`.
- The computer connected to the internet the first time you install things.

## Part 1 – Install OpenWebUI (only the first time)
1. In the terminal type `cd /home/stacy/AlphaOmega` and press Enter.
2. Type `./scripts/setup-openwebui.sh` and press Enter.
3. Wait until you see **"OpenWebUI Setup Complete"**. This can take a few minutes.

## Part 2 – Start the helper programs
1. In the same terminal type `./scripts/start.sh` and press Enter.
2. Watch the messages. When you see **"Agent-S (8001) is responsive"** everything needed for Agent-S is running.

## Part 3 – Start OpenWebUI
1. Open a **new** terminal window (again press `Ctrl` + `Alt` + `T`).
2. Type `cd /home/stacy/AlphaOmega` and press Enter.
3. Type `./scripts/start-openwebui.sh` and press Enter. Keep this window open; it shows OpenWebUI logs.

## Part 4 – Tell OpenWebUI about the AlphaOmega router
1. Open a **third** terminal window.
2. Type `cd /home/stacy/AlphaOmega` and press Enter.
3. Type `source venv/bin/activate` and press Enter.
4. Type `python register-pipeline.py` and press Enter. You should see **"Pipeline registered successfully"**.

## Part 5 – Pick the right model in the browser
1. Open your web browser and go to [http://localhost:8080](http://localhost:8080).
2. Log in if OpenWebUI asks you.
3. At the top left, click the model dropdown and choose **AlphaOmega Router**. (It might show up after refreshing the page.)
4. Click the gear icon ⚙️ → **Pipelines**. You should see **AlphaOmega Router** with the Agent-S address set to `http://localhost:8001`.

## Part 6 – Test that Agent-S responds
1. In OpenWebUI start a new chat.
2. Type something like **"Please take a screenshot of my screen"** and press Enter.
3. After a moment you should get a message with a picture of the screen. That means Agent-S is connected and working.

## If something goes wrong
- Make sure every terminal window still says it is running (no errors at the bottom).
- Visit [http://localhost:8001/health](http://localhost:8001/health). If you see `{"status":"ok"}` Agent-S is alive.
- If the browser does not show **AlphaOmega Router**, go back to Part 4 and re-run `python register-pipeline.py`.
- If the chat replies with an error, read the terminal that is running `start-openwebui.sh` for hints.

Great job! Agent-S is now ready to help inside OpenWebUI.
