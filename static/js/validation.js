function hide(element){
    document.getElementById(element).style.display = "none";
}
function show(element){
    document.getElementById(element).style.display = "block";}

function answer(){
    button = document.getElementById('answer_button');
    button.onclick = function() {hide('question')&show('ans')};
}

function initialize_add(){
    add_button = document.querySelectorAll('.add_button');
    for(const i of add_button)
    {
        i.onclick = add_deck;
    }
}

function add_deck(event){
    deck = event.target;
    deck_id = deck.dataset.deck_id;
    fetch('/dashboard/add_deck/'+deck_id).then(
        response => alert('Deck has been added you can find it on your Dashboard')
    ).catch(
        err => console.log(err)
        )
}

function new_deck(){
    button = document.getElementById('buttonfornew');
    button.onclick = function() {hide('alldecks')&show('new_deck')};
}


function validate(event){
    if(document.getElementById('radior').checked) { return true;}
    else if(document.getElementById('radiow').checked) { return true; }
    else {
        event.preventDefault()
        element = document.getElementById('answer_form')
        element.classList.add("was-validated");
        return false ;
        }
}

function confirmDelete() {
  var r = confirm("Are you sure!?!");
  if (r == true) {
  return true;
  } else {
  return false;
}
}