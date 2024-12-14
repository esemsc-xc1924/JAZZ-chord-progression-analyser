$(document).ready(function () {
    $(".chord-btn").click(function () {
        const chord = $(this).data("chord");
        const key = $("#key-select").val();

        // Send request to the backend
        $.ajax({
            type: "POST",
            url: "/generate_chord",
            contentType: "application/json",
            data: JSON.stringify({ key: key, chord: chord }),
            success: function (response) {
                if (response.audio_file) {
                    const audio = new Audio(response.audio_file);
                    audio.play();
                } else {
                    alert("No audio file generated.");
                }
            },
            error: function () {
                alert("Error generating chord audio.");
            },
        });
    });
});
