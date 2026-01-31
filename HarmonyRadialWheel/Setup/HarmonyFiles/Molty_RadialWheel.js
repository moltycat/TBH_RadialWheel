/* =========================================================
   Radial Wheel Host for Toon Boom Harmony
   - run only Molty_RadialWheel();
   - read commands from JSON and exec them
   ========================================================= */

function Molty_RadialWheel() {

    if (Molty_RadialWheel.running) return;
    Molty_RadialWheel.running = true;

    var commandFile = "C:/HarmonyRadialWheel/harmony_command.json";
    var tickTimer = new QTimer();

    tickTimer.timeout.connect(function () {
        try {
            var file = new QFile(commandFile);
            if (!file.exists()) return;
            if (!file.open(QIODevice.ReadOnly | QIODevice.Text)) return;

            var text = file.readAll();
            file.close();

            if (!text || text.length === 0) return;

            try {
                var command = JSON.parse(text);
                if (command && command.js) {
                    eval(command.js);
                    MessageLog.trace("✅ Executed: " + command.js);

                    if (file.open(QIODevice.WriteOnly | QIODevice.Truncate)) {
                        file.close();
                    }
                }
            } catch (e) {
                //MessageLog.trace("❌ Error parsing/executing command: " + e);
            }

        } catch (e) {
            //MessageLog.trace("❌ File read error: " + e);
        }
    });

    tickTimer.start(100); 
    MessageLog.trace("✅RadialWheelHost started✅");
	MessageBox.information("✅RadialWheelHost started✅");
}
