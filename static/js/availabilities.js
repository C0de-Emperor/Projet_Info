var maxLineNumber=0

function addLine(){
    console.log("add a new line")

    var availabilityColumn=document.getElementById("availabilityColumn");

    maxLineNumber++

    var newDiv=document.createElement("div")
    newDiv.classList.add("control")
    newDiv.classList.add("block-cube")
    newDiv.classList.add("block-input")
    newDiv.classList.add("availabilityInputBox")
    newDiv.setAttribute("name", String(maxLineNumber))
    newDiv.appendChild(document.createElement("text"))

    var dateInput=document.createElement("input")
    dateInput.type="datetime-local"
    dateInput.name="date"+String(maxLineNumber)
    dateInput.addEventListener("input", (element) => inputModified(element))
    newDiv.appendChild(dateInput)
    newDiv.appendChild(document.createElement("text"))

    var durationInput=document.createElement("input")
    durationInput.type="text"
    durationInput.name="duration"+String(maxLineNumber)
    durationInput.placeholder="durée (min)"
    durationInput.addEventListener("input", (element) => inputModified(element))
    newDiv.appendChild(durationInput)
    newDiv.appendChild(document.createElement("text"))
    
    var daysInRowInput=document.createElement("input")
    daysInRowInput.type="text"
    daysInRowInput.name="daysInARow"+String(maxLineNumber)
    daysInRowInput.placeholder="nb de jours d'affilée"
    daysInRowInput.addEventListener("input", (element) => inputModified(element))
    newDiv.appendChild(daysInRowInput)
    newDiv.appendChild(document.createElement("text"))

    var fieldNameInput=document.createElement("input")
    fieldNameInput.type="text"
    fieldNameInput.name="fieldName"+String(maxLineNumber)
    fieldNameInput.placeholder="nom du terrain"
    fieldNameInput.addEventListener("input", (element) => inputModified(element))
    newDiv.appendChild(fieldNameInput)
    newDiv.appendChild(document.createElement("text"))

    var subDiv=document.createElement("div")
    subDiv.classList.add("bg-inner")

    var div1=document.createElement("div")
    div1.classList.add("bg-top")
    div1.appendChild(subDiv)
    newDiv.appendChild(div1)
    newDiv.appendChild(document.createElement("text"))

    var div2=document.createElement("div")
    div2.classList.add("bg-right")
    div2.appendChild(subDiv)
    newDiv.appendChild(div2)
    newDiv.appendChild(document.createElement("text"))

    var div3=document.createElement("div")
    div3.classList.add("bg")
    div3.appendChild(subDiv)
    newDiv.appendChild(div3)

    availabilityColumn.insertBefore(newDiv, availabilityColumn.childNodes[maxLineNumber+1])

    var form = document.getElementsByTagName("form")[0]
    var formAction = form.action
    formAction=formAction.split("availabilitiesNumber=")[0]
    formAction=formAction+"availabilitiesNumber="+String(maxLineNumber)
    form.action=formAction

    console.log("lineAdded")
}

function removeLine(){
    let i=document.getElementsByClassName("availabilityInputBox").length-1
    var isBoxEmpty=true;

    while (i>0 && isBoxEmpty==true){
        targetedLine=document.getElementsByClassName("availabilityInputBox")[i]
        for (let k=1; k<=7; k=k+2){
            //console.log(targetedLine.childNodes[k].value);

            if (targetedLine.childNodes[k].value!=""){
                isBoxEmpty=false;
                break
            }
        }
        if(isBoxEmpty){
            document.getElementsByClassName("availabilityInputBox")[i].remove();
            maxLineNumber--
        }

        i--
    }

    addLine();
    
}

function inputModified(element){
    
    var targetedInput = element.target;
    var targetedLine = targetedInput.parentNode;


    var isBoxEmpty=true;
    for (let k=1; k<=7; k=k+2){
        //console.log(targetedLine.childNodes[k].value);

        if (targetedLine.childNodes[k].value!=""){isBoxEmpty=false;}
    }

    if (isBoxEmpty){
        removeLine()
    }
    else if (targetedLine.attributes[1].value==maxLineNumber){
        //console.log(targetedLine.attributes[1].value, targetedLine.parentNode)
        addLine()
    }

    console.log(targetedLine, targetedLine.attributes[1].value, maxLineNumber)
}

function initialize(){

    for(let n=0;n<document.getElementsByClassName("availabilityInputBox").length; n++){
        availabilityInputBox=document.getElementsByClassName("availabilityInputBox")[n]

        console.log(availabilityInputBox)
        for (let k=1; k<=7; k=k+2){
            console.log(availabilityInputBox.childNodes[k])

            availabilityInputBox.childNodes[k].addEventListener("input", (element) => inputModified(element))
        }
    }

    maxLineNumber=document.getElementsByClassName("availabilityInputBox").length-1

    addLine()
}

document.body.onload=initialize()