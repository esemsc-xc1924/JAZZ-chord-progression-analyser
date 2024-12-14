$(document).ready(function () {
    // Listen for chord button clicks
    $(".chord-btn").click(function () {
        const chord = $(this).data("chord"); // Get the chord (I, ii, etc.)
        const key = $("#key-select").val();  // Get the selected key

        // Send an AJAX POST request to the backend
        $.ajax({
            type: "POST",
            url: "/generate_chord",
            contentType: "application/json",
            data: JSON.stringify({ key: key, chord: chord }),
            success: function (response) {
                console.log("Chord generated:", response);
                // Play the audio if backend sends an audio file
                if (response.audio_file) {
                    const audio = new Audio(response.audio_file);
                    audio.play();
                } else {
                    alert("Chord generated successfully, but no audio file was provided.");
                }
            },
            error: function () {
                alert("Failed to generate chord. Please try again.");
            }
        });
    });
});
