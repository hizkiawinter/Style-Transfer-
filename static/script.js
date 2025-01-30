document.addEventListener("DOMContentLoaded", function() {
    const words = ["SUKSES."];
    let i = 0;
    let timer;

    function typingEffect() {
        let word = words[i].split("");
        let loopTyping = function() {
            if (word.length > 0) {
                document.getElementById("word").innerHTML += word.shift();
            } else {
                setTimeout(deletingEffect, 1000); // Pause before deleting
                return;
            }
            timer = setTimeout(loopTyping, 200); // Adjust speed of typing
        };
        loopTyping();
    }

    function deletingEffect() {
        let word = words[i].split("");
        let loopDeleting = function() {
            if (word.length > 0) {
                word.pop();
                document.getElementById("word").innerHTML = word.join("");
            } else {
                i = (i + 1) % words.length; // Cycle through words
                setTimeout(typingEffect, 500); // Pause before retyping
                return;
            }
            timer = setTimeout(loopDeleting, 100); // Adjust speed of deleting
        };
        loopDeleting();
    }

    typingEffect(); // Start effect
});
