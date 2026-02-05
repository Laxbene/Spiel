import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="1vs1 Neon Reaction", layout="centered")

def main():
    st.title("⚡ 1-vs-1 Neon Reaction")
    st.write("Spieler 1: **WASD + E** | Spieler 2: **Pfeiltasten + '-'**")

    # Das Spiel wird in einem IFrame via HTML/JS ausgeführt
    game_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            canvas { background: #111; border: 2px solid #555; display: block; margin: 0 auto; }
            .stats { color: white; font-family: sans-serif; display: flex; justify-content: space-around; }
        </style>
    </head>
    <body>
        <div class="stats">
            <p>Spieler 1 (Blau): <span id="s1">0</span> | Dash: <span id="c1">Bereit</span></p>
            <p>Spieler 2 (Rot): <span id="s2">0</span> | Dash: <span id="c2">Bereit</span></p>
        </div>
        <canvas id="gameCanvas" width="600" height="400"></canvas>

        <script>
            const canvas = document.getElementById("gameCanvas");
            const ctx = canvas.getContext("2d");

            // Spielzustand
            let p1 = { x: 50, y: 200, score: 0, color: '#00f', speed: 4, dashCd: 0 };
            let p2 = { x: 550, y: 200, score: 0, color: '#f00', speed: 4, dashCd: 0 };
            let goal = { x: 300, y: 200, size: 10 };
            
            const keys = {};
            window.addEventListener("keydown", e => keys[e.key.toLowerCase()] = true);
            window.addEventListener("keyup", e => keys[e.key.toLowerCase()] = false);

            function update() {
                // Spieler 1 Bewegung (WASD)
                if (keys['w'] && p1.y > 0) p1.y -= p1.speed;
                if (keys['s'] && p1.y < canvas.height) p1.y += p1.speed;
                if (keys['a'] && p1.x > 0) p1.x -= p1.speed;
                if (keys['d'] && p1.x < canvas.width) p1.x += p1.speed;
                
                // Spieler 1 Spezial (E) - Dash
                if (keys['e'] && p1.dashCd <= 0) {
                    p1.speed = 12;
                    p1.dashCd = 100; // Cooldown Frames
                    setTimeout(() => p1.speed = 4, 200);
                }

                // Spieler 2 Bewegung (Pfeiltasten)
                if (keys['arrowup'] && p2.y > 0) p2.y -= p2.speed;
                if (keys['arrowdown'] && p2.y < canvas.height) p2.y += p2.speed;
                if (keys['arrowleft'] && p2.x > 0) p2.x -= p2.speed;
                if (keys['arrowright'] && p2.x < canvas.width) p2.x += p2.speed;

                // Spieler 2 Spezial (-) - Dash
                if (keys['-'] && p2.dashCd <= 0) {
                    p2.speed = 12;
                    p2.dashCd = 100;
                    setTimeout(() => p2.speed = 4, 200);
                }

                // Cooldowns reduzieren
                if (p1.dashCd > 0) p1.dashCd--;
                if (p2.dashCd > 0) p2.dashCd--;

                // Kollision mit dem Ziel
                checkGoal(p1, "s1");
                checkGoal(p2, "s2");

                draw();
                requestAnimationFrame(update);
            }

            function checkGoal(p, spanId) {
                let dx = p.x - goal.x;
                let dy = p.y - goal.y;
                let distance = Math.sqrt(dx * dx + dy * dy);
                if (distance < 20) {
                    p.score++;
                    document.getElementById(spanId).innerText = p.score;
                    goal.x = Math.random() * (canvas.width - 40) + 20;
                    goal.y = Math.random() * (canvas.height - 40) + 20;
                }
            }

            function draw() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                // Ziel zeichnen
                ctx.fillStyle = "yellow";
                ctx.beginPath();
                ctx.arc(goal.x, goal.y, goal.size, 0, Math.PI*2);
                ctx.fill();

                // Spieler zeichnen
                ctx.fillStyle = p1.color;
                ctx.fillRect(p1.x-10, p1.y-10, 20, 20);
                ctx.fillStyle = p2.color;
                ctx.fillRect(p2.x-10, p2.y-10, 20, 20);

                // UI Update Cooldowns
                document.getElementById("c1").innerText = p1.dashCd <= 0 ? "Bereit" : "Warten...";
                document.getElementById("c2").innerText = p2.dashCd <= 0 ? "Bereit" : "Warten...";
            }

            update();
        </script>
    </body>
    </html>
    """
    
    components.html(game_html, height=500)

    st.info("""
    **Spielregeln:**
    - Wer zuerst 10 Punkte hat, gewinnt!
    - Die Spezialfähigkeit macht dich für einen Moment extrem schnell.
    - Achtung: Wenn du aus dem IFrame klickst, musst du wieder hineinklicken, damit die Tastatur reagiert.
    """)

if __name__ == "__main__":
    main()
