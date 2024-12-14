$(document).ready(function () {
    const progressionBar = document.getElementById("progression-bar");

    // Add single chord play functionality
    $(".chord-btn").click(function () {
        const chord = $(this).data("chord");
        const key = $("#key-select").val(); // Get the selected key from the dropdown

        // Send AJAX request to play the selected chord
        $.ajax({
            type: "POST",
            url: "/generate_chord",
            contentType: "application/json",
            data: JSON.stringify({ key, chord }),
            success: function (response) {
                if (response.audio_file) {
                    const audio = new Audio(response.audio_file);
                    audio.play();
                } else {
                    alert("Failed to generate chord audio.");
                }
            },
            error: function () {
                alert("Error communicating with the server.");
            }
        });
    });


    // Make buttons draggable
    $(".chord-btn").each(function () {
        this.draggable = true;

        this.addEventListener("dragstart", function (e) {
            e.dataTransfer.setData("text/plain", JSON.stringify({
                chord: this.dataset.chord,
                key: $("#key-select").val(),
                label: this.innerText
            }));
        });
    });

    // Enable dropping on the progression bar
    progressionBar.addEventListener("dragover", (e) => {
        e.preventDefault();
        progressionBar.classList.add("drag-over");
    });

    progressionBar.addEventListener("dragleave", () => {
        progressionBar.classList.remove("drag-over");
    });

    progressionBar.addEventListener("drop", (e) => {
        e.preventDefault();
        progressionBar.classList.remove("drag-over");

        // Get data from the dragged button
        const data = JSON.parse(e.dataTransfer.getData("text/plain"));
        const newButton = document.createElement("button");
        newButton.className = "chord-btn";
        newButton.innerText = `${data.key} ${data.chord}`;
        newButton.dataset.chord = data.chord;
        newButton.dataset.key = data.key;

        progressionBar.appendChild(newButton);
    });

    // Play the chord progression
    $("#play-progression").click(async function () {
        const progression = [];
        $("#progression-bar .chord-btn").each(function () {
            progression.push({
                chord: $(this).data("chord"),
                key: $(this).data("key"),
            });
        });

        if (progression.length === 0) {
            alert("No chords in the progression!");
            return;
        }

        for (const chord of progression) {
            await playChord(chord.key, chord.chord);
        }
    });

    // Function to play a single chord
    async function playChord(key, chord) {
        return new Promise((resolve) => {
            $.ajax({
                type: "POST",
                url: "/generate_chord",
                contentType: "application/json",
                data: JSON.stringify({ key, chord }),
                success: function (response) {
                    if (response.audio_file) {
                        const audio = new Audio(response.audio_file);
                        audio.play();
                        audio.onended = resolve;
                    } else {
                        alert("Failed to generate chord audio.");
                        resolve();
                    }
                },
                error: function () {
                    alert("Error generating chord audio.");
                    resolve();
                }
            });
        });
    }
});
