function show(id) {
    var hiddenDoc = $( "#dropdown" )
    var buttonImage = document.querySelector("#dropdown-btn i");
    if (hiddenDoc.css("max-height") === "0px") {
      buttonImage.style.transform = "rotate(0deg)";
      hiddenDoc.css("max-height", "200vh");
    } else {
      hiddenDoc.css("max-height", "0px")
      buttonImage.style.transform = "rotate(-90deg)"
    }
  }

  function phoneWarning(obj){
    if(obj.checked) {
      alert("Phone interviews are often unreliable and difficult for both the interviewer and the interviewee.\nWe highly discourage students from doing their interviews through the phone as they may affect their chances of receiving a scholarship.")
      var understood = prompt("I understand the risks associated with phone interviews. Please type in 'understood' to continue.", "");
        if (understood == null || understood.toLowerCase() != "understood"){
          obj.checked=false;
        }
      }
  }

// function show(id) {
//     var hiddenDoc = document.getElementById(id);
//     var button = document.getElementById('dropdown-btn');
//     var buttonImage = document.querySelector("#dropdown-btn i");
//     if (hiddenDoc.style.maxHeight === "0px") {
//       buttonImage.style.transform = "rotate(0deg)";
//       button.style.borderBottomRightRadius = "0px";
//       button.style.borderBottomLeftRadius = "0px";
//       hiddenDoc.style.maxHeight = "200vh";
//     } else {
//       hiddenDoc.style.maxHeight = "0px";
//       buttonImage.style.transform = "rotate(-90deg)"
//       setTimeout(function () {
//         button.style.borderBottomRightRadius = "10px";
//         button.style.borderBottomLeftRadius = "10px";
//     }, 1200);
//     }
//   }

function toggle_row(classname, button) {
    try {
      var hiddenDocs = document.getElementsByClassName(classname);
      var button = document.getElementById(button);
      for(var i=0; i<hiddenDocs.length; i++) {
          if (hiddenDocs[i].style.display == "none"){
            hiddenDocs[i].style.display = "table-row";
            button.style.color = "white";
            button.style.background = "var(--button)";
          } else {
            hiddenDocs[i].style.display = "none";
            button.style.background = "gold";
            button.style.color = "black";
          };
        }
        var rows = document.getElementsByTagName("table")[0].rows;
        var color1 = 'var(--rows1)';
        var color2 = 'var(--rows2)';
        var currentColor = color1;
        for(var i=1; i<rows.length; i++) {
          if (rows[i].style.display == "none"){
            continue;
          } else {
            rows[i].style.background = currentColor;
            if(currentColor == color1) {var currentColor = color2} else { var currentColor = color1};
          }
        }
        // var done = false
        // for(var i=rows.length-1; i>=1; i--) {
        //   var cells = rows[i].cells
        //   if (rows[i].style.display != "none" & !done){
        //     cells[0].style.borderBottomLeftRadius = "10px";
        //     cells[cells.length-1].style.borderBottomRightRadius = "10px";
        //     var done=true
        //   } else {
        //     cells[0].style.borderBottomLeftRadius = "0px";
        //     cells[cells.length-1].style.borderBottomRightRadius = "0px";
        //   }
        // }
    }
    catch(err) {
      alert('Error: no rows with this criteria found.');
      console.log(err);
    }
  }

