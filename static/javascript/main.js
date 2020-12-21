//console.log("starting script...")

const table = document.getElementsByClassName('table')[0];
console.log(table);

function createCard(number, ques){
  const card = document.createElement('div');
  card.className = "card";
  card.setAttribute("id",number);
  card.setAttribute("onclick", "cardClicked(this.id)");

  const sl_no = document.createElement('div');
  sl_no.innerText = number;
  const ques_name = document.createElement('div');
  ques_name.innerText = ques;

  card.append(sl_no);
  card.append(ques_name);

  return card;
}
