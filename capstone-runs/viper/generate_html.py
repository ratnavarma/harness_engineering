import re

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Viper: The Ultimate Canvas Snake Experience</title>
    <style>
        :root {
            --color-bg: #0f172a;
            --color-surface: #1e293b;
            --color-primary: #10b981;
            --color-primary-hover: #059669;
            --color-text: #f8fafc;
            --color-text-muted: #94a3b8;
            --color-border: #334155;
            --color-danger: #ef4444;
            --font-sans: system-ui, -apple-system, sans-serif;
            --spacing-1: 0.25rem;
            --spacing-2: 0.5rem;
            --spacing-3: 1rem;
            --spacing-4: 1.5rem;
            --spacing-5: 2rem;
            --spacing-6: 3rem;
            --spacing-8: 4rem;
            --spacing-12: 6rem;
            --radius-md: 0.375rem;
            --radius-lg: 0.5rem;
            --radius-xl: 1rem;
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        }
        [data-theme="light"] {
            --color-bg: #f8fafc;
            --color-surface: #ffffff;
            --color-text: #0f172a;
            --color-text-muted: #475569;
            --color-border: #e2e8f0;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: var(--font-sans);
            background-color: var(--color-bg);
            color: var(--color-text);
            line-height: 1.6;
            transition: background-color 0.3s, color 0.3s;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 var(--spacing-4);
        }
        section {
            padding: var(--spacing-12) 0;
            border-bottom: 1px solid var(--color-border);
        }
        section:last-child {
            border-bottom: none;
        }
        h1, h2, h3 { line-height: 1.2; margin-bottom: var(--spacing-4); color: var(--color-text); }
        h1 { font-size: 3rem; }
        h2 { font-size: 2.25rem; }
        h3 { font-size: 1.5rem; }
        p { margin-bottom: var(--spacing-4); font-size: 1.125rem; color: var(--color-text-muted); }
        a:focus-visible, button:focus-visible {
            outline: 2px solid var(--color-primary);
            outline-offset: 2px;
        }
        button {
            background-color: var(--color-primary);
            color: #fff;
            border: none;
            padding: var(--spacing-2) var(--spacing-4);
            font-size: 1rem;
            border-radius: var(--radius-md);
            cursor: pointer;
            transition: background-color 0.2s;
            font-family: inherit;
        }
        button:hover {
            background-color: var(--color-primary-hover);
        }
        button.secondary {
            background-color: var(--color-surface);
            color: var(--color-text);
            border: 1px solid var(--color-border);
        }
        button.secondary:hover {
            background-color: var(--color-border);
        }
        /* Navigation */
        nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: var(--spacing-4) 0;
            border-bottom: 1px solid var(--color-border);
        }
        .nav-links {
            display: flex;
            gap: var(--spacing-4);
        }
        .nav-links a {
            color: var(--color-text);
            text-decoration: none;
            font-weight: 500;
        }
        .nav-links a:hover {
            color: var(--color-primary);
        }
        /* Grid Layouts */
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr;
            gap: var(--spacing-8);
            align-items: center;
        }
        @media (min-width: 768px) {
            .grid-2 { grid-template-columns: 1fr 1fr; }
        }
        /* Game UI */
        .game-container {
            background-color: var(--color-surface);
            padding: var(--spacing-6);
            border-radius: var(--radius-xl);
            box-shadow: var(--shadow-md);
            text-align: center;
            border: 1px solid var(--color-border);
        }
        .game-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: var(--spacing-4);
            font-size: 1.25rem;
            font-weight: bold;
        }
        canvas {
            background-color: #000;
            border-radius: var(--radius-md);
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0 auto var(--spacing-4);
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.2);
        }
        .game-controls {
            display: flex;
            justify-content: center;
            gap: var(--spacing-4);
            flex-wrap: wrap;
        }
        /* FAQ Accordion */
        .accordion-item {
            border: 1px solid var(--color-border);
            border-radius: var(--radius-md);
            margin-bottom: var(--spacing-3);
            overflow: hidden;
        }
        .accordion-header {
            width: 100%;
            text-align: left;
            padding: var(--spacing-4);
            background-color: var(--color-surface);
            border: none;
            font-size: 1.125rem;
            font-weight: bold;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--color-text);
        }
        .accordion-content {
            padding: 0 var(--spacing-4);
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out, padding 0.3s ease;
            background-color: var(--color-bg);
        }
        .accordion-item.active .accordion-content {
            padding: var(--spacing-4);
            max-height: 500px;
        }
        .accordion-item.active .accordion-header {
            border-bottom: 1px solid var(--color-border);
        }
        /* SVGs */
        .svg-illustration {
            width: 100%;
            height: auto;
            max-width: 500px;
            display: block;
            margin: 0 auto;
        }
        /* Responsive */
        @media (max-width: 360px) {
            h1 { font-size: 2rem; }
            h2 { font-size: 1.75rem; }
            .nav-links { display: none; }
        }
        @media (min-width: 1280px) {
            .container { max-width: 1200px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <nav>
            <div style="font-size: 1.5rem; font-weight: bold; color: var(--color-primary);">Viper</div>
            <div class="nav-links">
                <a href="#game-section">Play</a>
                <a href="#about">About</a>
                <a href="#features">Features</a>
                <a href="#faq">FAQ</a>
            </div>
            <button id="theme-toggle" class="secondary" aria-label="Toggle Theme">Toggle Theme</button>
        </nav>
    </div>

    <!-- Section 1: Hero -->
    <section id="hero" class="container">
        <div class="grid-2">
            <div>
                <h1>Experience the Classic Snake Game Reimagined</h1>
                <p>Welcome to Viper, a modern, high-performance take on the beloved classic. Built with HTML5 Canvas and optimized for fluid gameplay, this is the snake game you remember, but better. Dive into a seamless experience where precision meets nostalgia.</p>
                <p>Whether you are a casual player looking to pass the time or a hardcore gamer aiming for the top of the leaderboards, Viper offers an engaging challenge that scales with your skill level. The mechanics are simple, but mastering the grid requires focus, quick reflexes, and strategic planning.</p>
                <button onclick="document.getElementById('game-section').scrollIntoView({behavior: 'smooth'})">Play Now</button>
            </div>
            <div>
                <!-- SVG 1: Product Artifact in Hero (Retro Arcade/Game Screen) -->
                <svg class="svg-illustration" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
                    <rect x="20" y="20" width="360" height="260" rx="15" fill="var(--color-surface)" stroke="var(--color-border)" stroke-width="4"/>
                    <rect x="40" y="40" width="320" height="200" rx="5" fill="#000"/>
                    <!-- Snake -->
                    <rect x="100" y="100" width="20" height="20" fill="var(--color-primary)"/>
                    <rect x="120" y="100" width="20" height="20" fill="var(--color-primary)"/>
                    <rect x="140" y="100" width="20" height="20" fill="var(--color-primary)"/>
                    <rect x="160" y="100" width="20" height="20" fill="var(--color-primary)"/>
                    <rect x="160" y="80" width="20" height="20" fill="var(--color-primary)"/>
                    <!-- Food -->
                    <circle cx="250" cy="150" r="10" fill="var(--color-danger)"/>
                    <!-- UI Elements -->
                    <text x="50" y="60" fill="var(--color-text)" font-family="monospace" font-size="14">SCORE: 120</text>
                    <text x="280" y="60" fill="var(--color-text)" font-family="monospace" font-size="14">HI: 450</text>
                </svg>
            </div>
        </div>
    </section>

    <!-- Section 2: Game -->
    <section id="game-section" class="container">
        <div class="game-container">
            <h2>Viper Arena</h2>
            <p>Use arrow keys or WASD to move. The snake speeds up every 5 foods you eat!</p>
            <div class="game-header">
                <span id="score-display">Score: 0</span>
                <span id="high-score-display">High Score: 0</span>
            </div>
            <canvas id="gameCanvas" width="400" height="400" tabindex="0"></canvas>
            <div class="game-controls">
                <button id="btn-start">Start Game</button>
                <button id="btn-pause" class="secondary">Pause</button>
                <button id="btn-restart" class="secondary">Restart</button>
            </div>
        </div>
    </section>

    <!-- Section 3: About -->
    <section id="about" class="container">
        <div class="grid-2">
            <div>
                <!-- SVG 2: Abstract representation of growth/snake -->
                <svg class="svg-illustration" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
                    <path d="M 50 250 Q 100 150 200 250 T 350 150" fill="none" stroke="var(--color-primary)" stroke-width="8" stroke-linecap="round"/>
                    <circle cx="350" cy="150" r="12" fill="var(--color-danger)"/>
                    <circle cx="50" cy="250" r="8" fill="var(--color-primary)"/>
                    <rect x="100" y="50" width="200" height="100" rx="10" fill="var(--color-surface)" stroke="var(--color-border)" stroke-width="2"/>
                    <text x="200" y="105" fill="var(--color-text)" font-family="sans-serif" font-size="24" text-anchor="middle">Evolution</text>
                </svg>
            </div>
            <div>
                <h2>About the Project</h2>
                <p>The concept of the snake game dates back to the late 1970s, originating with the arcade game Blockade. Since then, it has seen countless iterations, most notably becoming a staple on early mobile phones in the late 1990s. Viper is a tribute to this rich history, bringing the classic mechanics into the modern web era.</p>
                <p>We designed Viper to be more than just a simple clone. By utilizing the HTML5 Canvas API and the requestAnimationFrame method, we ensure that the game runs at a buttery smooth frame rate, free from the jitter and lag that plagued older web-based implementations. The game logic is decoupled from the rendering loop, allowing for precise control over the snake's speed and movement.</p>
                <p>Furthermore, Viper introduces a progressive difficulty curve. For every five pieces of food the snake consumes, the game speed increases slightly. This subtle change transforms the experience from a relaxing pastime into a frantic test of reflexes as your score climbs higher. It is a delicate balance of risk and reward, where every move must be calculated.</p>
            </div>
        </div>
    </section>

    <!-- Section 4: Features -->
    <section id="features" class="container">
        <h2>Core Features</h2>
        <div class="grid-2">
            <div>
                <p>Viper is packed with features designed to provide the best possible player experience. We have focused on performance, accessibility, and replayability to ensure that you keep coming back for more.</p>
                <p>First and foremost is the responsive design. Whether you are playing on a massive 4K monitor or a compact smartphone screen, the game scales perfectly to fit your device. The semantic HTML structure and CSS custom properties ensure that the UI is not only beautiful but also accessible to screen readers and keyboard users.</p>
                <p>Another key feature is the persistent high score system. By leveraging the browser's localStorage API, your highest score is saved locally on your device. This means you can close the browser, come back days later, and your record will still be there, waiting to be beaten. It adds a layer of personal competition that drives continuous improvement.</p>
                <p>Finally, the dynamic speed adjustment keeps the gameplay fresh. The game starts at a manageable pace, allowing you to get comfortable with the controls. But as you eat more food, the snake accelerates. This mechanic ensures that the game remains challenging, pushing your reaction times to the limit as you navigate the increasingly crowded arena.</p>
            </div>
            <div>
                <!-- SVG 3: Features/Gears -->
                <svg class="svg-illustration" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
                    <g stroke="var(--color-primary)" stroke-width="4" fill="none">
                        <circle cx="150" cy="150" r="60"/>
                        <circle cx="250" cy="100" r="40"/>
                        <circle cx="250" cy="220" r="30"/>
                        <path d="M 150 90 L 150 70 M 150 210 L 150 230 M 90 150 L 70 150 M 210 150 L 230 150"/>
                        <path d="M 107 107 L 93 93 M 193 193 L 207 207 M 193 107 L 207 93 M 107 193 L 93 207"/>
                    </g>
                    <circle cx="150" cy="150" r="20" fill="var(--color-surface)"/>
                    <circle cx="250" cy="100" r="15" fill="var(--color-surface)"/>
                    <circle cx="250" cy="220" r="10" fill="var(--color-surface)"/>
                </svg>
            </div>
        </div>
    </section>

    <!-- Section 5: Mechanics -->
    <section id="mechanics" class="container">
        <h2>Deep Dive into Mechanics</h2>
        <p>Understanding the underlying mechanics of Viper can give you a competitive edge. The game operates on a grid system, typically 20x20 cells. The snake and the food are snapped to this grid, ensuring that movements are predictable and precise. When you press an arrow key, you are not moving the snake immediately; rather, you are queuing a change in direction for the next tick of the game loop.</p>
        <p>The game loop is powered by requestAnimationFrame, a browser API that tells the browser you wish to perform an animation and requests that the browser calls a specified function to update an animation before the next repaint. This is vastly superior to older methods like setInterval, as it synchronizes with the display's refresh rate, preventing screen tearing and ensuring optimal performance.</p>
        <p>Collision detection is a critical component. The game must constantly check if the snake's head has intersected with the boundaries of the canvas or with its own body. If either condition is met, the game is over. Additionally, it checks if the head occupies the same grid cell as the food. If so, the snake grows by one segment, the score increases, and a new piece of food is spawned at a random, unoccupied location.</p>
        <p>The speed-up mechanic is implemented by tracking the number of foods eaten. We maintain a counter, and every time it reaches a multiple of five, we decrease the delay between game ticks. This means the requestAnimationFrame loop processes game logic more frequently, resulting in a faster-moving snake. It requires careful tuning to ensure the difficulty curve is steep enough to be challenging but not so abrupt that it feels unfair.</p>
    </section>

    <!-- Section 6: History -->
    <section id="history" class="container">
        <div class="grid-2">
            <div>
                <!-- SVG 4: History/Timeline -->
                <svg class="svg-illustration" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
                    <line x1="50" y1="150" x2="350" y2="150" stroke="var(--color-border)" stroke-width="4"/>
                    <circle cx="100" cy="150" r="10" fill="var(--color-primary)"/>
                    <circle cx="200" cy="150" r="10" fill="var(--color-primary)"/>
                    <circle cx="300" cy="150" r="10" fill="var(--color-primary)"/>
                    <text x="100" y="180" fill="var(--color-text)" font-family="sans-serif" font-size="14" text-anchor="middle">1976</text>
                    <text x="200" y="180" fill="var(--color-text)" font-family="sans-serif" font-size="14" text-anchor="middle">1997</text>
                    <text x="300" y="180" fill="var(--color-text)" font-family="sans-serif" font-size="14" text-anchor="middle">Today</text>
                    <text x="100" y="130" fill="var(--color-text-muted)" font-family="sans-serif" font-size="12" text-anchor="middle">Blockade</text>
                    <text x="200" y="130" fill="var(--color-text-muted)" font-family="sans-serif" font-size="12" text-anchor="middle">Mobile Era</text>
                    <text x="300" y="130" fill="var(--color-text-muted)" font-family="sans-serif" font-size="12" text-anchor="middle">Web Canvas</text>
                </svg>
            </div>
            <div>
                <h2>The Legacy of Snake</h2>
                <p>The lineage of the snake game is a fascinating journey through the history of video games. It began in 1976 with a two-player arcade game called Blockade, developed by Gremlin Industries. In Blockade, players controlled characters that left a solid trail behind them, and the goal was to survive longer than the opponent without crashing into a wall or a trail. This fundamental mechanic laid the groundwork for everything that followed.</p>
                <p>Throughout the 1980s, variations of the game appeared on early personal computers, often under names like Nibbler or Worm. These versions introduced the single-player survival aspect and the concept of eating items to grow longer. However, it wasn't until 1997 that the game truly exploded into mainstream consciousness.</p>
                <p>Nokia, a dominant force in the mobile phone market at the time, included a version of Snake on their Nokia 6110 handset. Programmed by Taneli Armanto, this simple, monochrome game became an instant phenomenon. It was accessible, addictive, and perfectly suited to the limited input methods of a mobile phone keypad. Millions of people around the world spent countless hours trying to beat their high scores, cementing Snake's status as a cultural icon.</p>
                <p>Today, the legacy continues with modern interpretations like Viper. While the graphics have improved and the platforms have evolved, the core appeal remains unchanged. It is a testament to the enduring power of simple, elegant game design. Viper honors this legacy by preserving the classic feel while leveraging modern web technologies to deliver the definitive snake experience.</p>
            </div>
        </div>
    </section>

    <!-- Section 7: Benefits -->
    <section id="benefits" class="container">
        <h2>Cognitive Benefits of Playing</h2>
        <p>While often dismissed as a simple distraction, playing games like Viper can actually offer several cognitive benefits. The fast-paced nature of the game requires intense focus and rapid decision-making, which can help improve hand-eye coordination and reaction times. As the snake speeds up, players must anticipate future movements and plan their path accordingly, engaging their spatial reasoning skills.</p>
        <p>Furthermore, the pursuit of a high score fosters a growth mindset. Players learn from their mistakes, analyze their failures, and develop new strategies to improve their performance. This iterative process of trial and error is a fundamental aspect of learning and problem-solving. When you crash into a wall, you immediately understand why it happened and how to avoid it in the next round.</p>
        <p>Playing Viper can also serve as a form of stress relief. The immersive nature of the gameplay can provide a temporary escape from the pressures of daily life, allowing players to enter a state of 'flow' where they are fully absorbed in the task at hand. This focused attention can be meditative, helping to clear the mind and reduce anxiety. It is a productive way to take a break and recharge your mental batteries.</p>
        <p>Finally, the accessibility of the game means that these benefits are available to everyone. You don't need expensive hardware or hours of free time to enjoy Viper. A quick five-minute session during a lunch break is enough to stimulate your brain and provide a satisfying sense of accomplishment. It is a small but meaningful way to incorporate cognitive exercise into your daily routine.</p>
    </section>

    <!-- Section 8: FAQ -->
    <section id="faq" class="container">
        <h2>Frequently Asked Questions</h2>
        <div class="accordion">
            <div class="accordion-item">
                <button class="accordion-header" aria-expanded="false">
                    How do I control the snake?
                    <span class="icon">+</span>
                </button>
                <div class="accordion-content">
                    <p>You can control the snake using the arrow keys on your keyboard (Up, Down, Left, Right) or the WASD keys (W for Up, S for Down, A for Left, D for Right). On touch devices, swipe gestures are currently not supported in this version, but keyboard navigation is fully optimized.</p>
                </div>
            </div>
            <div class="accordion-item">
                <button class="accordion-header" aria-expanded="false">
                    How does the scoring system work?
                    <span class="icon">+</span>
                </button>
                <div class="accordion-content">
                    <p>You earn 10 points for every piece of food the snake consumes. As your score increases, the game keeps track of your highest score achieved on your current device. This high score is saved automatically and will persist even if you close your browser, thanks to the localStorage API.</p>
                </div>
            </div>
            <div class="accordion-item">
                <button class="accordion-header" aria-expanded="false">
                    Why does the game get faster?
                    <span class="icon">+</span>
                </button>
                <div class="accordion-content">
                    <p>To provide a progressive challenge, the snake's movement speed increases slightly every time you eat 5 pieces of food. This mechanic ensures that the game remains engaging and tests your reflexes as you progress. The speed cap is designed to be extremely challenging but technically possible for skilled players.</p>
                </div>
            </div>
            <div class="accordion-item">
                <button class="accordion-header" aria-expanded="false">
                    Can I pause the game?
                    <span class="icon">+</span>
                </button>
                <div class="accordion-content">
                    <p>Yes! You can pause the game at any time by clicking the "Pause" button below the game canvas, or by pressing the 'P' key on your keyboard. Pressing it again will resume the game from where you left off. This is perfect for when you need to take a quick break.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Section 9: CTA / Footer -->
    <section id="cta" class="container" style="text-align: center;">
        <h2>Ready to Test Your Reflexes?</h2>
        <p>Join thousands of players who have already experienced the thrill of Viper. Whether you are aiming for a new high score or just looking for a fun way to pass the time, the arena awaits. Do you have what it takes to master the grid?</p>
        <button onclick="document.getElementById('game-section').scrollIntoView({behavior: 'smooth'})" style="font-size: 1.25rem; padding: var(--spacing-3) var(--spacing-6);">Play Viper Now</button>
        <div style="margin-top: var(--spacing-8); color: var(--color-text-muted); font-size: 0.875rem;">
            <p>&copy; 2024 Viper Game Studios. Built with HTML5 Canvas and Vanilla JavaScript.</p>
            <p>Designed with semantic HTML, CSS custom properties, and a focus on performance and accessibility.</p>
        </div>
    </section>

    <script>
        // Interactive Behavior 1: Theme Toggle
        const themeToggleBtn = document.getElementById('theme-toggle');
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.body.getAttribute('data-theme');
            if (currentTheme === 'light') {
                document.body.removeAttribute('data-theme');
            } else {
                document.body.setAttribute('data-theme', 'light');
            }
        });

        // Interactive Behavior 2: FAQ Accordion
        const accordionHeaders = document.querySelectorAll('.accordion-header');
        accordionHeaders.forEach(header => {
            header.addEventListener('click', () => {
                const item = header.parentElement;
                const isActive = item.classList.contains('active');
                
                // Close all
                document.querySelectorAll('.accordion-item').forEach(i => {
                    i.classList.remove('active');
                    i.querySelector('.accordion-header').setAttribute('aria-expanded', 'false');
                    i.querySelector('.icon').textContent = '+';
                });

                // Open clicked if it wasn't active
                if (!isActive) {
                    item.classList.add('active');
                    header.setAttribute('aria-expanded', 'true');
                    item.querySelector('.icon').textContent = '-';
                }
            });
        });

        // Interactive Behavior 3: Snake Game
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreDisplay = document.getElementById('score-display');
        const highScoreDisplay = document.getElementById('high-score-display');
        const btnStart = document.getElementById('btn-start');
        const btnPause = document.getElementById('btn-pause');
        const btnRestart = document.getElementById('btn-restart');

        // Game Constants
        const gridSize = 20;
        const tileCount = canvas.width / gridSize;
        
        // Game State
        let snake = [];
        let food = {};
        let dx = 0;
        let dy = 0;
        let score = 0;
        let highScore = localStorage.getItem('viperHighScore') || 0;
        let gameLoopId;
        let isPaused = false;
        let isGameOver = false;
        let isPlaying = false;
        let foodsEaten = 0;
        
        // Speed control
        let baseSpeed = 150; // ms per frame
        let currentSpeed = baseSpeed;
        let lastRenderTime = 0;

        highScoreDisplay.textContent = `High Score: ${highScore}`;

        function initGame() {
            snake = [
                { x: 10, y: 10 },
                { x: 10, y: 11 },
                { x: 10, y: 12 }
            ];
            dx = 0;
            dy = -1;
            score = 0;
            foodsEaten = 0;
            currentSpeed = baseSpeed;
            scoreDisplay.textContent = `Score: ${score}`;
            isGameOver = false;
            isPaused = false;
            isPlaying = true;
            spawnFood();
            btnStart.disabled = true;
            canvas.focus();
            if (gameLoopId) cancelAnimationFrame(gameLoopId);
            requestAnimationFrame(gameLoop);
        }

        function spawnFood() {
            let newFood;
            while (true) {
                newFood = {
                    x: Math.floor(Math.random() * tileCount),
                    y: Math.floor(Math.random() * tileCount)
                };
                // Check if food spawned on snake
                const onSnake = snake.some(segment => segment.x === newFood.x && segment.y === newFood.y);
                if (!onSnake) break;
            }
            food = newFood;
        }

        function gameLoop(currentTime) {
            if (isPaused || isGameOver || !isPlaying) return;

            gameLoopId = requestAnimationFrame(gameLoop);

            const secondsSinceLastRender = (currentTime - lastRenderTime);
            if (secondsSinceLastRender < currentSpeed) return;

            lastRenderTime = currentTime;

            update();
            draw();
        }

        function update() {
            const head = { x: snake[0].x + dx, y: snake[0].y + dy };

            // Wall collision
            if (head.x < 0 || head.x >= tileCount || head.y < 0 || head.y >= tileCount) {
                gameOver();
                return;
            }

            // Self collision
            for (let i = 0; i < snake.length; i++) {
                if (head.x === snake[i].x && head.y === snake[i].y) {
                    gameOver();
                    return;
                }
            }

            snake.unshift(head);

            // Food collision
            if (head.x === food.x && head.y === food.y) {
                score += 10;
                foodsEaten++;
                scoreDisplay.textContent = `Score: ${score}`;
                
                // Speed up every 5 foods
                if (foodsEaten % 5 === 0) {
                    currentSpeed = Math.max(50, currentSpeed - 15);
                }
                
                spawnFood();
            } else {
                snake.pop();
            }
        }

        function draw() {
            // Clear canvas
            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Draw grid (optional, for aesthetics)
            ctx.strokeStyle = '#111';
            for(let i=0; i<tileCount; i++) {
                ctx.beginPath();
                ctx.moveTo(i*gridSize, 0);
                ctx.lineTo(i*gridSize, canvas.height);
                ctx.stroke();
                ctx.beginPath();
                ctx.moveTo(0, i*gridSize);
                ctx.lineTo(canvas.width, i*gridSize);
                ctx.stroke();
            }

            // Draw food
            ctx.fillStyle = 'var(--color-danger)';
            ctx.beginPath();
            ctx.arc(food.x * gridSize + gridSize/2, food.y * gridSize + gridSize/2, gridSize/2 - 2, 0, Math.PI * 2);
            ctx.fill();

            // Draw snake
            snake.forEach((segment, index) => {
                ctx.fillStyle = index === 0 ? 'var(--color-primary)' : 'var(--color-primary-hover)';
                ctx.fillRect(segment.x * gridSize + 1, segment.y * gridSize + 1, gridSize - 2, gridSize - 2);
            });
        }

        function gameOver() {
            isGameOver = true;
            isPlaying = false;
            btnStart.disabled = false;
            
            if (score > highScore) {
                highScore = score;
                localStorage.setItem('viperHighScore', highScore);
                highScoreDisplay.textContent = `High Score: ${highScore}`;
            }

            ctx.fillStyle = 'rgba(0, 0, 0, 0.75)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = 'var(--color-text)';
            ctx.font = '30px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('GAME OVER', canvas.width / 2, canvas.height / 2);
            ctx.font = '20px sans-serif';
            ctx.fillText(`Score: ${score}`, canvas.width / 2, canvas.height / 2 + 40);
        }

        function togglePause() {
            if (!isPlaying || isGameOver) return;
            isPaused = !isPaused;
            if (isPaused) {
                btnPause.textContent = 'Resume';
                ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = 'var(--color-text)';
                ctx.font = '30px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('PAUSED', canvas.width / 2, canvas.height / 2);
            } else {
                btnPause.textContent = 'Pause';
                lastRenderTime = performance.now();
                requestAnimationFrame(gameLoop);
            }
        }

        // Event Listeners
        btnStart.addEventListener('click', initGame);
        btnRestart.addEventListener('click', initGame);
        btnPause.addEventListener('click', togglePause);

        window.addEventListener('keydown', e => {
            if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '].includes(e.key)) {
                if(document.activeElement === canvas) {
                    e.preventDefault();
                }
            }

            if (!isPlaying || isPaused) {
                if (e.key.toLowerCase() === 'p' && isPlaying) togglePause();
                return;
            }

            switch (e.key) {
                case 'ArrowUp':
                case 'w':
                case 'W':
                    if (dy !== 1) { dx = 0; dy = -1; }
                    break;
                case 'ArrowDown':
                case 's':
                case 'S':
                    if (dy !== -1) { dx = 0; dy = 1; }
                    break;
                case 'ArrowLeft':
                case 'a':
                case 'A':
                    if (dx !== 1) { dx = -1; dy = 0; }
                    break;
                case 'ArrowRight':
                case 'd':
                case 'D':
                    if (dx !== -1) { dx = 1; dy = 0; }
                    break;
                case 'p':
                case 'P':
                    togglePause();
                    break;
            }
        });

        // Initial draw
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = 'var(--color-text)';
        ctx.font = '20px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Press Start Game to Play', canvas.width / 2, canvas.height / 2);
    </script>
</body>
</html>
"""

with open("index.html", "w") as f:
    f.write(html_template)

# Word count check
text_content = re.sub('<[^<]+>', ' ', html_template)
words = text_content.split()
print(f"Word count: {len(words)}")
