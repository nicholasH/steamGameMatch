
var friDiv = document.getElementsByClassName("friendDiv");

function print_printFriend(n)
          {
            console.log(n);
          }

async function populateFriends(){

        var friendArray = await eel.getMyFriends()();
        for (var i =0; i < friendArray.length; i++)
        {
            var friendInfo = friendArray[i];

            var btn = document.createElement("div");

            btn.className = "btn";

            var img = document.createElement("IMG");
            img.src =  friendInfo.avatarfull;
            img.className = "img-responsive";

            var p = document.createElement("p");
            p.textContent = friendInfo.personaname;

            var input = document.createElement("input");
            input.className = "selectFriend";
            input.setAttribute("name","selectFriend");
            input.setAttribute("type","checkbox");
            input.id = friendInfo.steamid;
            input.value = friendInfo.steamid;

            btn.appendChild(img)
            btn.appendChild(p)
            btn.appendChild(input)

            friDiv[0].appendChild(btn);

            console.log(friendInfo);
        }
}

async function populateFriendsGames()
{
     console.log("populating Games");
    var commonGamesDiv = document.getElementById("commonGamesDiv");
    var selectFriends = document.getElementsByClassName("selectFriend");

    var child = commonGamesDiv.lastElementChild;
        while (child) {
            commonGamesDiv.removeChild(child);
            child = commonGamesDiv.lastElementChild;
            }


    var selected = [];

    for(var i =0; i < selectFriends.length; i++)
    {
        if(selectFriends[i].checked)
        {
            selected.push(selectFriends[i].id)
        }
    }

    var games = await eel.getMyCommonGames(selected)();
    console.log(games);

    for(var i =0; i < games.length; i++){
        var game = games[i];

        var gameDiv = document.createElement("div");
        gameDiv.className = "game show";


        var gameImg = document.createElement("img");
        gameImg.src = game.header_image;
        gameImg.className = "img-responsive"

        var gameName = document.createElement("p");
        gameName.textContent = game.name;

        var metaDiv = document.createElement("div");
        metaDiv.className = "GameMeta";
        metaDiv.setAttribute("style","display: none;")


        var cat = game.categories

        console.log(game);
        for(var j =0; j < cat.length; j++){

            var catID = document.createElement("p");
            var catDis = document.createElement("p")

            catID.className = "catID";
            catID.textContent = cat[j].id;
            catDis.className = "catDis";
            catDis.textContent = cat[j].description;

            metaDiv.appendChild(catID)
            metaDiv.appendChild(catDis)
        }

        gameDiv.appendChild(gameImg);
        gameDiv.appendChild(gameName);
        gameDiv.appendChild(metaDiv)

        commonGamesDiv.appendChild(gameDiv)
    }

}

function showAll(){
    var header = document.getElementById("commonGamesDiv");
    var games = header.getElementsByClassName("game");

    for(var i = 0; i < games.length; i++){
        games[i].classList.remove("hidden");
        games[i].classList.add("show");
     }
}

function showRan(){
    var ranDiv = document.getElementById("getRanGame");
    ranDiv.classList.remove("hidden");
    ranDiv.classList.add("show");
}

function showCoOp(){
    var header = document.getElementById("commonGamesDiv");
    var games = header.getElementsByClassName("game");

    for(var i = 0; i < games.length; i++){
        var isCoOp = false

        var meta = games[i].getElementsByClassName("GameMeta")
        var ids = meta[0].getElementsByClassName("catID")

            for(var x =  0;x < ids.length; x++){
                id = ids[x]

                //if not in list
                if ('38' === id.textContent) {
                    isCoOp = true
                }
            }

        if(!isCoOp){
            games[i].classList.remove("show");
            games[i].classList.add("hidden");
        }
     }
}

function getMuti() {
    var header = document.getElementById("commonGamesDiv");
    var games = header.getElementsByClassName("game");

    for(var i = 0; i < games.length; i++){
        var isMulti = false

        var meta = games[i].getElementsByClassName("GameMeta")
        var ids = meta[0].getElementsByClassName("catID")

            for(var x =  0;x < ids.length; x++){
                id = ids[x]

                //if not in list
                if (['1', '20', '27','36','38'].indexOf(id.textContent) >= 0) {
                    isMulti = true
                }
            }

        if(!isMulti){
            games[i].classList.remove("show");
            games[i].classList.add("hidden");
        }
        else{
            games[i].classList.remove("hidden");
            games[i].classList.add("show");
        }
     }
}

function getRandom(){
    showRan();
    var header = document.getElementById("commonGamesDiv");
    var games = header.getElementsByClassName("game");
    var randomDiv = document.getElementById("randomGame");


    var shownGames =[]
    for(var i = 0; i < games.length; i++){
        if(games[i].classList.contains("show")){
            shownGames.push(games[i])
        }
     }
     while (randomDiv.firstChild) {
        randomDiv.removeChild(randomDiv.firstChild);
     }
     var gameDiv = shownGames[Math.floor(Math.random() * shownGames.length)]
     randomDiv.appendChild(gameDiv.cloneNode(true))
}
function loading(form){
    form.submit.disabled = true;
    form.submit.innerHTML = "Please wait...";
  }

populateFriends()
