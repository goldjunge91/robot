### Phase 1: Grundlagen & Hardware-Aufbau 🔩

In dieser Phase wird das physische Fundament des Roboters geschaffen. Alle mechanischen und elektrischen Komponenten werden zusammengebaut und verbunden, um eine testbereite Hardware-Plattform zu schaffen.

* **Aufgabe 1.1: Mechanischer Aufbau des Chassis**
  * **Beschreibung & Ziel:** Das Ziel ist der Zusammenbau des mechanischen Grundgerüsts. Dazu werden die Motoren und die Mecanum-Räder fest mit dem Chassis verbunden. Ein stabiles und korrekt ausgerichtetes Chassis ist die Voraussetzung für präzise omnidirektionale Bewegungen.
  * **Vorgehen:**
        1. Befestige die vier DC-Getriebemotoren sicher an den vorgesehenen Halterungen des Chassis.
        2. Montiere die vier Mecanum-Räder auf den Achsen der Motoren. Achte dabei auf die korrekte Ausrichtung der Rollen (typischerweise bilden sie ein X- oder O-Muster, wenn man von oben auf den Roboter blickt).
        3. Platziere die Hauptkomponenten (Pis, Akku, Treiberplatinen) provisorisch auf dem Chassis, um ein Gefühl für die Gewichtsverteilung und den Platzbedarf zu bekommen.
  * **Erfolgs-Kriterium (Outcome):** Das Roboter-Chassis steht stabil auf seinen vier Rädern. Alle mechanischen Teile sind fest montiert und die Räder lassen sich von Hand frei drehen.

* **Aufgabe 1.2: Aufbau der zentralen Stromversorgung**
  * **Beschreibung & Ziel:** Ziel ist es, eine sichere und stabile Stromversorgung für alle elektronischen Komponenten zu gewährleisten. Eine saubere Verkabelung verhindert Kurzschlüsse und sorgt für die Langlebigkeit der Bauteile.
  * **Vorgehen:**
        1. Verbinde das 3S Li-Ion Akkupack mit der Batterieschutzplatine (BMS).
        2. Schließe den Ausgang des BMS an den Eingang des INA3221 Stromsensors an.
        3. Verkabel den Ausgang des Stromsensors mit den Spannungseingängen der Motortreiber (TB6612FNG) und den Spannungswandlern (Buck Converters), die den Raspberry Pi 4B und den Pico versorgen.
        4. **Sicherheitscheck:** Überprüfe die Polarität (+/-) aller Verbindungen mehrfach mit einem Multimeter, *bevor* der Akku angeschlossen wird.
  * **Erfolgs-Kriterium (Outcome):** Wenn der Akku angeschlossen wird, leuchten die Power-LEDs des Raspberry Pi 4B und des Pico. Die Spannung an den Motortreibern entspricht der Akkuspannung. Es tritt kein Rauch oder übermäßige Hitze auf.

* **Aufgabe 1.3: Verkabelung der Motorsteuerung und Encoder**
  * **Beschreibung & Ziel:** Hier wird die Verbindung zwischen dem "Muskel" (Motor) und dem "Kleinhirn" (Pico) hergestellt. Der Pico muss in der Lage sein, den Motoren Befehle zu senden (über die Treiber) und deren exakte Bewegung zu messen (über die Encoder).
  * **Vorgehen:**
        1. Verbinde die GPIO-Pins des Raspberry Pi Pico mit den Steuereingängen (PWM, IN1, IN2) der vier TB6612FNG Motortreiber.
        2. Verbinde die Ausgänge der Motortreiber mit den Anschlüssen der vier DC-Motoren.
        3. Verbinde die Signalausgänge der Hall-Encoder von jedem Motor mit separaten GPIO-Eingängen am Pico.
  * **Erfolgs-Kriterium (Outcome):** Alle elektrischen Verbindungen zwischen Pico, Motortreibern und Motoren sind hergestellt und dokumentiert (z.B. in einer Tabelle mit Pin-Belegungen).

---

### Phase 2: Low-Level-Steuerung (Raspberry Pi Pico) 🧠

Der Raspberry Pi Pico wird programmiert, um die Echtzeit-Aufgaben der Motorsteuerung zu übernehmen. Er wird zur zuverlässigen ausführenden Instanz, die präzise Befehle umsetzt.

* **Aufgabe 2.1: Ansteuerung der DC-Motoren**
  * **Beschreibung & Ziel:** Es soll ein grundlegendes MicroPython/CircuitPython-Skript erstellt werden, das die Motoren zum Leben erweckt. Dies bestätigt, dass die Verkabelung aus Phase 1 korrekt ist und die Motortreiber wie erwartet funktionieren.
  * **Vorgehen:**
        1. Installiere MicroPython/CircuitPython auf dem Pico und richte die Entwicklungsumgebung ein.
        2. Schreibe ein Testskript, das per PWM-Signal die Geschwindigkeit eines einzelnen Motors steuert und dessen Drehrichtung ändert.
        3. Erweitere das Skript, sodass alle vier Motoren gleichzeitig und individuell angesteuert werden können.
  * **Erfolgs-Kriterium (Outcome):** Du kannst über das Skript auf dem Pico jeden Motor einzeln mit unterschiedlichen Geschwindigkeiten vorwärts und rückwärts drehen lassen.

* **Aufgabe 2.2: Auslesen der Rad-Encoder**
  * **Beschreibung & Ziel:** Ziel ist es, die von den Hall-Encodern erzeugten Impulse zu erfassen und in eine physikalische Größe (Drehgeschwindigkeit) umzurechnen. Dies ist die Grundlage für jede Form der geregelten und kontrollierten Bewegung.
  * **Vorgehen:**
        1. Schreibe eine Funktion, die Interrupts nutzt, um die steigenden und fallenden Flanken der Encoder-Signale zu zählen (Ticks).
        2. Implementiere einen Timer, der in regelmäßigen Abständen (z.B. alle 20ms) die Anzahl der gezählten Ticks ausliest und daraus die Geschwindigkeit in "Ticks pro Sekunde" berechnet.
  * **Erfolgs-Kriterium (Outcome):** Wenn du ein Rad manuell drehst, gibt das Pico-Skript die korrekte Drehgeschwindigkeit und -richtung auf der Konsole aus.

* **Aufgabe 2.3: Implementierung einer Drehzahlregelung (PID)**
  * **Beschreibung & Ziel:** Motoren laufen ohne Regelung je nach Last und Akkuspannung unterschiedlich schnell. Ein PID-Regler sorgt dafür, dass ein Motor eine vorgegebene Zielgeschwindigkeit exakt einhält. Dies ist der wichtigste Schritt für präzise Fahrmanöver.
  * **Vorgehen:**
        1. Implementiere eine PID-Regelungs-Schleife für einen Motor. Sie vergleicht die *Soll-Geschwindigkeit* mit der *Ist-Geschwindigkeit* (aus Aufgabe 2.2) und passt das PWM-Signal kontinuierlich an, um die Differenz zu minimieren.
        2. Finde durch Experimentieren geeignete Werte für die PID-Parameter (P, I, D), sodass der Motor schnell und ohne Überschwingen seine Zielgeschwindigkeit erreicht.
        3. Wende den Regler auf alle vier Motoren an.
  * **Erfolgs-Kriterium (Outcome):** Du kannst im Code eine Zielgeschwindigkeit (z.B. 500 Ticks/Sekunde) für jedes Rad festlegen, und die Räder halten diese Geschwindigkeit präzise, auch wenn du sie leicht mit der Hand abbremst.

* **Aufgabe 2.4: Entwicklung der seriellen Kommunikationsschnittstelle**
  * **Beschreibung & Ziel:** Der Pico muss mit dem Raspberry Pi 4B kommunizieren können. Es wird ein einfaches, aber robustes Protokoll entwickelt, um Bewegungsbefehle zu empfangen und Messwerte (Odometrie) zu senden.
  * **Vorgehen:**
        1. Definiere ein einfaches Text-basiertes Format für die serielle Kommunikation über USB, z.B. `v:vx,vy,omega\n` zum Empfangen und `o:w1,w2,w3,w4\n` zum Senden der Radgeschwindigkeiten.
        2. Implementiere auf dem Pico den Code, der die serielle Schnittstelle auf eingehende Befehle überwacht, diese parst und die Werte an die PID-Regler weitergibt.
        3. Sende in der Hauptschleife des Picos kontinuierlich die aktuellen, gemessenen Radgeschwindigkeiten zurück an den Sender.
  * **Erfolgs-Kriterium (Outcome):** Du kannst von einem seriellen Monitor auf deinem PC einen Befehl (z.B. `v:0.5,0,0`) an den Pico senden. Daraufhin beginnen sich die Räder zu drehen, und der Pico sendet die gemessenen Geschwindigkeiten zurück an den PC.

---

### Phase 3: High-Level-Setup & Teleoperation 🎮

In dieser Phase wird der Raspberry Pi 4B als Gehirn des Roboters konfiguriert und die Brücke zur Low-Level-Steuerung geschlagen. Das Ergebnis ist ein manuell fernsteuerbarer Roboter.

* **Aufgabe 3.1: Grundinstallation des Raspberry Pi 4B mit ROS2**
  * **Beschreibung & Ziel:** Das Betriebssystem und die Roboter-Software-Architektur (ROS2) müssen auf dem High-Level-Controller installiert und konfiguriert werden. Dies schafft die Software-Umgebung für alle nachfolgenden Aufgaben.
  * **Vorgehen:**
        1. Installiere ein empfohlenes Betriebssystem (z.B. Ubuntu 22.04) auf der SD-Karte des Pi 4B.
        2. Folge der offiziellen Anleitung, um eine passende ROS2-Distribution (z.B. Humble, Iron) zu installieren.
        3. Konfiguriere das Netzwerk (WLAN) und aktiviere SSH, um drahtlos auf den Pi zugreifen zu können.
  * **Erfolgs-Kriterium (Outcome):** Du kannst dich per SSH mit dem Pi 4B verbinden und ROS2-Demoprogramme (z.B. `talker`/`listener`) erfolgreich ausführen.

* **Aufgabe 3.2: Erstellung der ROS2-Kommunikationsbrücke zum Pico**
  * **Beschreibung & Ziel:** Es wird ein ROS2-Knoten geschrieben, der als Übersetzer zwischen der abstrakten ROS2-Welt und der konkreten Hardware-Welt des Picos fungiert. Dieser Knoten ist die zentrale Schnittstelle zur Roboterbasis.
  * **Vorgehen:**
        1. Erstelle ein neues ROS2-Paket.
        2. Schreibe darin einen Python- oder C++-Knoten, der das `geometry_msgs/Twist` Topic abonniert (der Standard in ROS2 für Geschwindigkeitsbefehle).
        3. Immer wenn eine `Twist`-Nachricht empfangen wird, berechnet der Knoten die inverse Kinematik für die Mecanum-Räder, um die individuellen Radgeschwindigkeiten zu ermitteln.
        4. Formatiere diese Radgeschwindigkeiten gemäß dem in Aufgabe 2.4 definierten Protokoll und sende sie über die serielle Schnittstelle an den Pico.
        5. Lies gleichzeitig die vom Pico gesendeten Odometrie-Daten, wandle sie in eine `nav_msgs/Odometry`-Nachricht um und veröffentliche diese in ROS2.
  * **Erfolgs-Kriterium (Outcome):** Wenn du manuell eine `Twist`-Nachricht mit `ros2 topic pub` veröffentlichst, bewegen sich die Räder des Roboters. Gleichzeitig kannst du mit `ros2 topic echo` die vom Knoten veröffentlichten Odometrie-Daten sehen.

* **Aufgabe 3.3: Integration der Gamepad-Fernsteuerung (Teleoperation)**
  * **Beschreibung & Ziel:** Der Roboter soll intuitiv und manuell steuerbar werden. Dazu wird ein Xbox-Controller in das ROS2-System eingebunden, um die Bewegungen des Roboters direkt zu kontrollieren.
  * **Vorgehen:**
        1. Installiere das ROS2-Paket `joy` und `teleop_twist_joy`.
        2. Konfiguriere `teleop_twist_joy` so, dass die Achsen des Xbox-Controllers den linearen (Vx, Vy) und rotatorischen (Vomega) Geschwindigkeiten der `Twist`-Nachricht zugeordnet werden.
        3. Starte den `joy_node`, den `teleop_twist_joy`-Knoten und deinen Kommunikationsbrücken-Knoten aus Aufgabe 3.2.
  * **Erfolgs-Kriterium (Outcome):** Der Roboter lässt sich flüssig und in alle Richtungen (vorwärts, seitwärts, diagonal, rotierend) mit dem Xbox-Controller steuern.

---

### Phase 4: Sensorintegration & SLAM 🗺️

Der Roboter lernt zu "sehen". Durch die Integration der Sensoren wird er in die Lage versetzt, seine Umgebung wahrzunehmen und eine Karte davon zu erstellen.

* **Aufgabe 4.1: Integration von LiDAR und IMU in ROS2**
  * **Beschreibung & Ziel:** Die primären Navigationssensoren müssen in ROS2 eingebunden werden, damit ihre Daten für höhere Algorithmen zur Verfügung stehen. Dies ist der Schritt von einem rein ferngesteuerten zu einem wahrnehmenden System.
  * **Vorgehen:**
        1. Schließe den LiDAR-Sensor und die IMU-Einheit physisch an den Raspberry Pi 4B an (meist über USB oder I2C/SPI).
        2. Installiere und konfiguriere die jeweiligen ROS2-Treiber für beide Sensoren.
        3. Starte die Treiber und überprüfe mit `ros2 topic list` und `ros2 topic echo`, ob die Sensordaten korrekt auf den Topics `/scan` (für LiDAR) und `/imu` (für IMU) veröffentlicht werden.
        4. Visualisiere die Daten im ROS2-Tool `rviz2`, um zu bestätigen, dass die Umgebungsscans und die Ausrichtungsdaten sinnvoll sind.
  * **Erfolgs-Kriterium (Outcome):** In `rviz2` wird der 360°-Scan des LiDARs als Punktwolke und die Ausrichtung der IMU als 3D-Modell in Echtzeit korrekt angezeigt.

* **Aufgabe 4.2: Erstellung des Roboter-Modells (URDF)**
  * **Beschreibung & Ziel:** ROS2 muss wissen, wie der Roboter physisch aufgebaut ist. Eine URDF-Datei (Unified Robot Description Format) beschreibt die einzelnen Teile des Roboters (Chassis, Räder) und vor allem die exakte Position und Ausrichtung der Sensoren relativ zur Roboterbasis. Dies ist **zwingend erforderlich** für SLAM und Navigation.
  * **Vorgehen:**
        1. Erstelle eine neue URDF-Datei. Definiere darin die `base_link` (das Chassis) als zentrales Element.
        2. Füge `links` für die Räder und die Sensoren (LiDAR, IMU) hinzu.
        3. Definiere `joints`, die diese `links` miteinander verbinden. Miss die exakten Abstände (x, y, z) der Sensoren vom Mittelpunkt des Roboters und trage sie hier ein.
        4. Lade die URDF-Datei mit dem `robot_state_publisher`-Knoten und visualisiere das Ergebnis in `rviz2`.
  * **Erfolgs-Kriterium (Outcome):** In `rviz2` wird ein 3D-Modell deines Roboters angezeigt. Die visualisierten LiDAR-Scans (aus Aufgabe 4.1) entspringen exakt der Position, an der der LiDAR im 3D-Modell platziert ist.

* **Aufgabe 4.3: Erstellung einer Umgebungskarte (SLAM)**
  * **Beschreibung & Ziel:** SLAM (Simultaneous Localization and Mapping) ist der Prozess, bei dem der Roboter eine Karte einer unbekannten Umgebung erstellt und sich gleichzeitig innerhalb dieser Karte lokalisiert. Das Ergebnis ist der digitale Zwilling der realen Umgebung.
  * **Vorgehen:**
        1. Installiere und konfiguriere ein ROS2 SLAM-Paket, z.B. `slam_toolbox`.
        2. Starte alle bisherigen Knoten: die Robotersteuerung, die Sensortreiber, den `robot_state_publisher` und den `slam_toolbox`-Knoten.
        3. Fahre den Roboter langsam und vorsichtig mit dem Gamepad durch den Raum oder die Wohnung, die kartiert werden soll. Beobachte in `rviz2`, wie die Karte in Echtzeit aufgebaut wird.
        4. Wenn der Bereich vollständig erkundet ist, speichere die Karte mit den Werkzeugen des SLAM-Pakets.
  * **Erfolgs-Kriterium (Outcome):** Du hast eine 2D-Karte (typischerweise als `.yaml`- und `.pgm`-Datei) gespeichert, die den Grundriss der Umgebung genau abbildet.

---

### Phase 5: Autonome Navigation 🎯

Der Roboter lernt, die erstellte Karte zu nutzen, um selbstständig Pfade zu planen und Ziele zu erreichen, während er Hindernissen ausweicht.

* **Aufgabe 5.1: Konfiguration des ROS2 Navigation Stacks (Nav2)**
  * **Beschreibung & Ziel:** Der Nav2-Stack ist das Gehirn für die autonome Navigation in ROS2. Er muss für die spezifischen Eigenschaften deines Roboters (Größe, Geschwindigkeit, Sensoren) konfiguriert werden, um intelligent agieren zu können.
  * **Vorgehen:**
        1. Installiere den `nav2_bringup`-Stack.
        2. Erstelle eine eigene Nav2-Konfigurationsdatei. Lade darin die in Aufgabe 4.3 erstellte Karte.
        3. Passe die Parameter für den globalen und lokalen Planer sowie die Kostenkarten (`costmap`) an die Abmessungen und die Dynamik deines Roboters an. Trage die Sensor-Topics (z.B. `/scan`) als Beobachtungsquellen ein.
        4. Integriere den VL53L0X-Sensor, indem du seine Daten als zusätzliche `RangeSensorLayer` in die Kostenkarte einfügst, um die Erkennung von nahen Hindernissen zu verbessern.
  * **Erfolgs-Kriterium (Outcome):** Du kannst den Nav2-Stack starten, ohne dass Fehler auftreten. In `rviz2` wird die Karte geladen, der Roboter lokalisiert sich korrekt darauf und es werden Kostenkarten (Bereiche um Hindernisse) visualisiert.

* **Aufgabe 5.2: Test der autonomen Punkt-zu-Punkt-Navigation**
  * **Beschreibung & Ziel:** Dies ist der ultimative Test der bisherigen Arbeit. Der Roboter soll einen Befehl erhalten, zu einem bestimmten Punkt zu fahren, und diesen Befehl komplett selbstständig ausführen.
  * **Vorgehen:**
        1. Starte den gesamten Navigations-Stack.
        2. Verwende das "2D Goal Pose"-Werkzeug in `rviz2`, um dem Roboter ein Ziel auf der Karte vorzugeben.
        3. Beobachte, wie der Roboter einen Pfad plant (als grüne Linie in `rviz2` sichtbar) und diesem Pfad folgt.
        4. Stelle während der Fahrt ein unvorhergesehenes Hindernis (z.B. einen Karton) in den Weg und prüfe, ob der Roboter stoppt oder einen neuen Pfad plant.
  * **Erfolgs-Kriterium (Outcome):** Der Roboter fährt zuverlässig zu dem in `rviz2` gesetzten Zielpunkt und weicht dabei sowohl den in der Karte verzeichneten als auch neuen, unvorhergesehenen Hindernissen aus.

---

### Phase 6: Computer Vision & Nerf-Launcher 👁️

In dieser Phase wird der interaktive Teil des Projekts umgesetzt. Der Roboter erhält die Fähigkeit, seine Umgebung nicht nur zu vermessen, sondern auch Objekte darin zu erkennen und darauf zu reagieren.

* **Aufgabe 6.1: Hardware-Aufbau und Low-Level-Steuerung des Launchers**
  * **Beschreibung & Ziel:** Der Nerf-Launcher wird mechanisch montiert und elektrisch mit dem Pico verbunden. Der Pico erhält die Fähigkeit, den Launcher präzise auszurichten und die Flywheel-Motoren zu starten.
  * **Vorgehen:**
        1. Baue die Pan/Tilt-Servos, die Brushless-Motoren und die Kamera zu einer Einheit zusammen und montiere sie auf dem Roboter.
        2. Verbinde die Servos und die ESCs der Brushless-Motoren mit freien GPIO-Pins am Pico.
        3. Erweitere den MicroPython-Code auf dem Pico um Funktionen zur Ansteuerung der Servos (z.B. `servo.angle(90)`) und zum Senden von PWM-Signalen an die ESCs.
        4. Erweitere das serielle Protokoll um Befehle zum Zielen und Feuern (z.B. `t:pan,tilt\n` und `f:1\n`).
  * **Erfolgs-Kriterium (Outcome):** Du kannst über eine serielle Verbindung Befehle an den Pico senden, um den Launcher auf eine bestimmte Gradzahl auszurichten und die Flywheels auf Knopfdruck hochdrehen zu lassen.

* **Aufgabe 6.2: Implementierung der Gesichtserkennung**
  * **Beschreibung & Ziel:** Es wird ein ROS2-Knoten entwickelt, der das Kamerabild analysiert, um menschliche Gesichter zu finden. Dies ist die Wahrnehmungsgrundlage für die automatische Zielerfassung.
  * **Vorgehen:**
        1. Installiere OpenCV für Python auf dem Raspberry Pi 4B.
        2. Starte einen ROS2-Knoten (`usb_cam`), der das Bild der USB-Kamera auf dem Topic `/image_raw` veröffentlicht.
        3. Schreibe einen neuen ROS2-Knoten, der `/image_raw` abonniert.
        4. Wende in diesem Knoten einen vortrainierten Gesichtserkennungs-Algorithmus von OpenCV (z.B. Haar-Kaskaden oder ein DNN-Modell) auf jedes eingehende Bild an.
        5. Wenn ein Gesicht erkannt wird, veröffentliche die Koordinaten des umgebenden Rechtecks (bounding box) auf einem neuen ROS2-Topic (z.B. `/detected_face`).
  * **Erfolgs-Kriterium (Outcome):** Wenn eine Person vor die Kamera tritt, veröffentlicht der Knoten die Pixel-Koordinaten des erkannten Gesichts. Du kannst dies mit `ros2 topic echo /detected_face` überprüfen. In einem optionalen Schritt kann das Bild mit dem gezeichneten Rechteck auf einem anderen Topic zur Visualisierung veröffentlicht werden.

* **Aufgabe 6.3: Implementierung der automatischen Zielverfolgung**
  * **Beschreibung & Ziel:** Die erkannten Gesichtskoordinaten werden nun genutzt, um den Nerf-Launcher automatisch auf das Ziel auszurichten. Dies verbindet die Computer Vision mit der Aktorik.
  * **Vorgehen:**
        1. Schreibe einen weiteren ROS2-Knoten (`aiming_controller`), der das `/detected_face` Topic abonniert.
        2. Berechne in diesem Knoten die Abweichung des Mittelpunkts der Bounding-Box von der Bildmitte.
        3. Übersetze diese Pixel-Abweichung mithilfe einer einfachen Proportionalregelung (P-Regler) in Korrekturbefehle für die Pan- und Tilt-Servos.
        4. Sende diese Befehle über die serielle Brücke (Aufgabe 3.2) an den Pico, der dann den Launcher entsprechend ausrichtet.
  * **Erfolgs-Kriterium (Outcome):** Wenn sich eine Person vor dem Roboter bewegt, verfolgt der Nerf-Launcher das Gesicht automatisch und versucht, es in der Mitte des Kamerabildes zu halten.

---

### Phase 7: Finalisierung & Systemintegration ✨

In der letzten Phase werden alle Einzelteile zu einem robusten und benutzerfreundlichen Gesamtsystem zusammengefügt und das Projekt wird sauber dokumentiert.

* **Aufgabe 7.1: Einrichtung der Systemüberwachung (Batterie)**
  * **Beschreibung & Ziel:** Um den Roboter sicher betreiben zu können, ist es wichtig, den Ladezustand des Akkus zu kennen. Der INA3221-Sensor wird ausgelesen und seine Daten werden im ROS2-System verfügbar gemacht.
  * **Vorgehen:**
        1. Verbinde den I2C-Bus des INA3221 mit dem Raspberry Pi 4B.
        2. Schreibe einen ROS2-Knoten, der die Sensor-Bibliothek nutzt, um Spannung und Strom auszulesen.
        3. Veröffentliche diese Werte in regelmäßigen Abständen auf einem Topic, z.B. als `sensor_msgs/BatteryState`.
  * **Erfolgs-Kriterium (Outcome):** Du kannst den aktuellen Batteriestand und den Stromverbrauch des Roboters jederzeit mit `ros2 topic echo` abfragen.

* **Aufgabe 7.2: Erstellung von Start-Skripten (Launch-Files)**
  * **Beschreibung & Ziel:** Ein komplexes ROS2-System besteht aus vielen einzelnen Knoten. Launch-Files ermöglichen es, das gesamte System – von den Treibern über die Navigation bis zur Gesichtserkennung – mit einem einzigen Befehl zu starten. Dies erhöht die Benutzerfreundlichkeit enorm.
  * **Vorgehen:**
        1. Erstelle eine zentrale ROS2-Launch-Datei in Python oder XML.
        2. Füge dieser Datei Einträge für alle benötigten Knoten hinzu (Pico-Brücke, Sensor-Treiber, `robot_state_publisher`, Nav2, Gesichtserkennung usw.).
        3. Organisiere die Launch-Files modular, sodass du z.B. nur die Navigation oder nur den Launcher-Teil separat starten kannst.
  * **Erfolgs-Kriterium (Outcome):** Mit einem einzigen Befehl (`ros2 launch mein_roboter_paket mein_roboter.launch.py`) startet der komplette Roboter und ist nach kurzer Zeit voll einsatzbereit.

* **Aufgabe 7.3: Projektdokumentation**
  * **Beschreibung & Ziel:** Ein gutes Projekt ist ein gut dokumentiertes Projekt. Die Dokumentation sichert dein Wissen, macht den Code für andere verständlich und bildet den formalen Abschluss der Arbeit.
  * **Vorgehen:**
        1. Säubere und kommentiere den gesamten von dir geschriebenen Code.
        2. Erstelle eine `README.md`-Datei für dein Code-Repository, die erklärt, wie man das Projekt installiert, konfiguriert und startet.
        3. Schreibe einen Abschlussbericht, der die Architektur, die Herausforderungen und die Ergebnisse des Projekts beschreibt.
        4. Erstelle ein kurzes Video, das die Kernfunktionen des Roboters demonstriert: Teleoperation, SLAM, autonome Navigation und die automatische Zielverfolgung mit dem Nerf-Launcher.
  * **Erfolgs-Kriterium (Outcome):** Eine vollständige, verständliche und nachvollziehbare Dokumentation des gesamten Projekts liegt vor.
