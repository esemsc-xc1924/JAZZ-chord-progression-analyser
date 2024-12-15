$(document).ready(function () {
    const progressionBar = document.getElementById("progression-bar");

    // Update diatonic chord names when the key or naming mode changes
    function updateChordNames() {
        const selectedKey = $("#key-select").val();
        const namingMode = $("#naming-mode").val();

        // Loop through all chord buttons and update their names
        $(".chord-btn").each(function () {
            const button = $(this); // Reference to the chord button
            const chord = button.data("chord");

            // Send AJAX request to get the updated chord name for the new key
            $.ajax({
                type: "POST",
                url: "/generate_chord",
                contentType: "application/json",
                data: JSON.stringify({ key: selectedKey, chord }),
                success: function (response) {
                    if (response.status === "success") {
                        const displayChord = namingMode === "roman" ? response.display_chord_numeral : response.display_chord;
                        button.text(displayChord); // Update button text
                    } else {
                        console.error("Failed to update chord for new key:", chord);
                    }
                },
                error: function () {
                    console.error("Error updating chord for new key:", chord);
                }
            });
        });

        // Update dropped chords in the progression bar
        $("#progression-bar .dropped-chord").each(async function () {
            const button = $(this);
            const chord = button.data("originalChord");
            const key = button.data("originalKey");

            const response = await fetch("/generate_chord", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ key, chord }),
            });
            const result = await response.json();

            if (result.status === "success") {
                const displayChord = namingMode === "roman" ? result.display_chord_numeral : result.display_chord;
                button.innerText = displayChord;
            }
        });
    }

    // Listen for key change or naming mode toggle
    $("#key-select, #naming-mode").change(updateChordNames);

    // Add single chord play functionality
    // Add single chord play functionality
$(".chord-btn").click(function () {
    const button = $(this);
    const chord = button.data("chord");
    const key = $("#key-select").val();
    const namingMode = $("#naming-mode").val(); // Get current naming mode

    $.ajax({
        type: "POST",
        url: "/generate_chord",
        contentType: "application/json",
        data: JSON.stringify({ key, chord }),
        success: function (response) {
            if (response.status === "success") {
                const audioFile = response.audio_file; // Ensure audio file is retrieved correctly
                const displayChord = namingMode === "roman" ? response.display_chord_numeral : response.display_chord;
                
                // Play the audio file
                const audio = new Audio(audioFile);
                audio.play();

                // Update button text based on the naming mode
                button.text(displayChord);
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

    progressionBar.addEventListener("drop", async (e) => {
        e.preventDefault();
        progressionBar.classList.remove("drag-over");

        // Get data from the dragged button
        const data = JSON.parse(e.dataTransfer.getData("text/plain"));

        // Create a container div for the chord and delete button
        const chordContainer = document.createElement("div");
        chordContainer.className = "chord-container";

        // Create the chord button
        const newButton = document.createElement("button");
        newButton.className = "chord-btn dropped-chord";
        newButton.dataset.originalKey = data.key;
        newButton.dataset.originalChord = data.chord;

        // Fetch the display chord name from the backend
        const response = await fetch("/generate_chord", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                key: data.key,
                chord: data.chord 
            }),
        });
        const result = await response.json();

        if (result.status === "success") {
            const namingMode = $("#naming-mode").val();
            newButton.innerText = namingMode === "roman" ? result.display_chord_numeral : result.display_chord;
        } else {
            newButton.innerText = `${data.key} ${data.chord}`;
        }

        // Create the delete button
        const deleteButton = document.createElement("button");
        deleteButton.className = "delete-btn";
        deleteButton.innerText = "✖";
        deleteButton.onclick = function () {
            chordContainer.remove();
        };

        // Append buttons to container
        chordContainer.appendChild(newButton);
        chordContainer.appendChild(deleteButton);
        progressionBar.appendChild(chordContainer);
    });

    $("#play-progression").click(async function () {
        const progression = [];
        $("#progression-bar .chord-btn").each(function () {
            progression.push($(this).data("originalChord")); // Collect only the chord names
        });
    
        if (progression.length === 0) {
            alert("No chords in the progression!");
            return;
        }
    
        // Play each chord in the progression
        for (const chord of progression) {
            const key = $("#key-select").val(); // Assume all chords share the selected key
            await playChord(key, chord);
        }
    
        // Send progression to the backend to find a matching song
// Send progression to the backend to find a matching song
        const response = await fetch("/match_song", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ progression }), // Send progression as a JSON array
        });
        const result = await response.json();

        if (result.status === "success") {
            const matchedSongs = result.songs; // Expecting an array of songs
            if (Array.isArray(matchedSongs) && matchedSongs.length > 0) {
                // Create a list of songs to display
                const songList = matchedSongs.map(song => `<li>${song}</li>`).join("");
                $("#chord-info-content").html(`<ul>${songList}</ul>`); // Display as a list
            } else {
                $("#chord-info-content").text("No matching songs found");
            }
        } else {
            $("#chord-info-content").text("An error occurred while fetching songs");
        }
    });
    

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
