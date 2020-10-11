/*************************************************
JavaScript for Illustrator 
『グラフ作成 for Splatoo2』

試合データCSVファイルを読み込んで、
ダイアログから描画するグラフを選択し、
選択した範囲内に描画します。

試合データCSVはikaMatchStatus.pyなどで取得できます。

作成者：こんやがやまだ
2020_10_01	v1.0
*************************************************/

////////// 各種設定 ////////////////////////////////////////////////////
// 軸線の色
var colorScale = [128, 128, 128];

// フォント
var fontScale = 'RowdyStd-EB';
var fontSizeScale = 28;
var colorTextScale = [255, 255, 255];

var colorGraph = [255, 0, 255];
var colorYellow = [251, 176, 59];
var colorBlue = [41, 171, 226];
var colorLine = [colorYellow, colorBlue];

var colorY = [255, 255, 0];
var colorC = [0, 255, 255];
var colorBack = [colorYellow, colorBlue];

// グラフ軸線の太さ
var lineWidthAxis = 3;
var lineWidthScale = 1;

// アサリの数の目盛線間隔
var yScaleClam = 5;

//////////////////////////////////////////////////////////////
/* メイン処理 */
// CSVファイルを開く
var fileObj = File.openDialog("CSVファイルを指定してください", '*.csv');

var flagFile = false;
// CSVファイルが指定されたか
if ( !fileObj ){ 
    alert( makeMessage( "noFile" ) );
}else{
    // ステータス・カウントファイルを読み込む
    var returnList = readFiles(fileObj);

    // ファイルを読み込めたかどうか
    if ( returnList ){
        var statusList = returnList[0];
        var countList  = returnList[1];

        // データのルールとfps
        var rule = statusList[1][0];
        var fps  = statusList[1][3];

        flagFile = true;
    }
}

var flagDialog = false;
// ファイルを正しく読み込めたか
if (flagFile) {
    makeDialogSetting(rule);
    flagDialog =true;
}




//////////////////////////////////////////////////////////////
/* ステータス・カウントファイルを読み込む */
function readFiles(fileObj) {
    // 指定したファイルの種類を判別する
    var fileName = fileObj.fullName;
    var fileType = fileName.slice(-10, -4);
    var statusObj, countObj;

    // ファイルの種類に応じて場合分け
    switch (fileType) {
        case '_count':
            var csvPath = fileObj.fullName.slice(0, -9) + 'status.csv';
            statusObj = new File(csvPath);
            countObj = fileObj;
            break;
    
        case 'status':
            var csvPath = fileObj.fullName.slice(0, -11) + '_count.csv';
            countObj = new File(csvPath);
            statusObj = fileObj;
            break;

        default:
            alert( makeMessage("err1") );
            return undefined;
    }

    // ステータス・カウントファイルが存在するか
    if ( !statusObj.exists || !countObj.exists ) {
        alert( makeMessage("err2") );
    }else{
        var statusList = readCSV(statusObj);
        var countList  = readCSV(countObj);
        
        statusObj.close();
        countObj.close();
        fileObj.close();

        return [statusList, countList]; 
    }       
}





/*
// グラフタイトルとグラフエリアを取得
var docObj = app.activeDocument;
var selObj = docObj.selection;
var len = selObj.length;

var maxWidthSelObj = 0;
for (var index=0; index<len; index++){
  selObj[index].selected = false;
  objType = selObj[index].typename;

  switch (objType) {
    case "TextFrame":
        titleObj = selObj[index];
        
      break;

    case "PathItem":
        selObj[index].selected = false;
        var bounds = selObj[index].geometricBounds;
        var widthSelObj = bounds[2] - bounds[0]; 

        if (widthSelObj > maxWidthSelObj){
          graphAreaObj = selObj[index];
          maxWidthSelObj = widthSelObj;
        }

      break;

    default:
      break;
  }
}

titleObj.selected = true;
graphAreaObj.selected = true;

// グラフ描画エリア（長方形）のサイズ取得
graphAreaObj.filled = false;
graphAreaObj.stroked = false;

var geo = graphAreaObj.geometricBounds;
var areaLeft   = geo[0];
var areaTop    = geo[1];
var areaRight  = geo[2];
var areaBottom = geo[3];

// グラフ本体の左上座標と大きさを決定
var xOrigin = areaLeft + fontSizeScale * 2.5;
var yOrigin = areaTop - fontSizeScale * 0.5;    // y座標はマイナス
var pointOrigin = [xOrigin, yOrigin];
var widthGraph = areaRight - areaLeft - fontSizeScale * 4;
var heightGraph = areaTop - areaBottom - fontSizeScale * 2;
*/
/*
┌────────────────────────────────────────────────────┐
│       ┌──────────────────────────────────────────┐ │
│       │                                          │ │ 
│       │                                          │ │
│       │                                          │ │
│       │                                          │ │
│       │                                          │ │
│       └──────────────────────────────────────────┘ │   
│                                                    │  
└────────────────────────────────────────────────────┘ 
*/
/*
switch (ddnObj.selection.index) {
    case 0:
        drawScale("plain");
        break;
    case 1:
        if ( checkLine1.value ){
            drawScale("count");
        }else{
            drawScale("plain");
        }
        break;

    case 2:
        if ( checkLine1.value ){
            drawScale("count");
        }else if ( checkLine2.value ){
            maxClam = Math.max.apply(null, countLineList1.concat(countLineList2));
            drawScale("position", maxClam);
        }else{
            drawScale("plain");
        }
        break;

    case 3:
        if ( checkLine1.value ){
            drawScale("count");
        }else if ( checkLine2.value ){
            maxClam = Math.max.apply(null, countLineList1.concat(countLineList2));
            drawScale("position", maxClam);
        }else{
            drawScale("plain");
        }
        break;

    case 4:
        ctrlList = [];
        for (i=1; i<countList.length; i++){
            ctrlList.push(countList[i][1]);
        }
        lengthMatch = ctrlList.length;

        tmpList = setLineList();
        countLineList1 = tmpList[0];
        countLineList2 = tmpList[1];
        
        if ( checkLine1.value ){
            drawScale("count");
        }else if ( checkLine2.value ){
            maxClam = Math.max.apply(null, countLineList1.concat(countLineList2));
            drawScale("clam", maxClam);
        }else{
            drawScale("plain");
        }


        lineNum = Math.floor(maxClam / 5) + 1;
        yScaleMax = lineNum * 5;
  

        for (index=0; index<2; index++){
            var countLineList = tmpList[index];
            if (countLineList.length > 0){
                ptlist = makeLinePointList(countLineList, yScaleMax);
                drawLine(ptlist, colorLine[index], 5);
            }
        }
        
        if ( checkBack1.value ){
            // コントロール状況に応じて背景描画
            ctrlPre = ctrlList[0];
            TL = [0, 0];
            for (i=2; i<lengthMatch; i++){
                var x = i / lengthMatch * widthGraph;
                var ctrlNow = ctrlList[i];

                if (ctrlNow != ctrlPre){
                    if (ctrlPre == 1){
                        BR = [x, -heightGraph];
                        drawRectangle(TL, BR, 'false', colorBack[0]);

                    }else if (ctrlPre == 2){
                        BR = [x, -heightGraph];
                        drawRectangle(TL, BR, 'false', colorBack[1]);
                    }

                    if (ctrlNow != 0){
                        TL = [x, 0];
                    }
                }

                ctrlPre = ctrlNow;
            }   
        }   

        titleObj.contents = "アサリ保有数の推移";

        break;

        
}


////////////////////////////////////////////////////////////////////////////////////////////
function setLineList() {
    var countLineList1 = [];
    var countLineList2 = [];

    if ( checkLine1.value ){
        if ( checkLine1A.value ){
            for (i=1; i<countList.length; i++){
                countLineList1.push(countList[i][2]);
            }
        }
        if ( checkLine1B.value ){
            for (i=1; i<countList.length; i++){
                countLineList1.push(countList[i][3]);
            }
        }

    }else if ( checkLine2.value ){
        if ( checkLine2A.value ){
            var countLineList1 = [];
            for (i=1; i<countList.length; i++){
                countLineList1.push(countList[i][8]);
            }
        }

        if ( checkLine2B.value ){
            var countLineList2 = [];
            for (i=1; i<countList.length; i++){
                countLineList2.push(countList[i][9]);
            }
        }
    }

    return [countLineList1, countLineList2];
}
*/

/* グラフの各種軸線・目盛線を描画する */
function drawScale(scaleType, maxClamNum) {
    // 水平方向の線の場合分け
    switch ( scaleType ) {
        case "count":
            // 目盛線の位置
            yScaleList = []
            for (i=0; i<=5; i++){
                var y = (1 - i/5) * heightGraph * (-1);
                var text = i/5 * 100;
                var lineWidth = lineWidthScale;
                yScaleList.push([y, lineWidth, text]);
            }

            // 横軸は下端
            yScaleList[0][1] = lineWidthAxis;

            break;

        case "position":
            // 目盛線の位置・線幅・数字を設定
            yScaleList = []
            for (i=0; i<=4; i++){
                var y = (1 - i/4) * heightGraph * (-1); 
                var text = Math.abs( (2 - i) * 50 );    // 100, 50, 0, 50, 100
                var lineWidth = lineWidthScale;
                yScaleList.push([y, lineWidth, text]);
            }

            // 横軸は下端
            yScaleList[2][1] = lineWidthAxis;

            break;

        case "clam":
            // 目盛線の位置・線幅・数字を設定
            yScaleList = []
            lineNum = Math.floor(maxClamNum / yScaleClam) + 1;
            for (i=0; i<=lineNum; i++){
                var y = (1 -i/lineNum) * heightGraph * (-1);
                var text = i * yScaleClam;
                var lineWidth = lineWidthScale;
                yScaleList.push([y, lineWidth, text]);
            }

            // 横軸は下端
            yScaleList[0][1] = lineWidthAxis;

            break;

        case "plain":
            // 目盛線の位置・線幅・数字を設定
            yScaleList = []
            for (i=0; i<=5; i++){
                var y = (1 - i/5) * heightGraph * (-1);
                var text = " ";
                var lineWidth = lineWidthScale;
                yScaleList.push([y, lineWidth, text]);
            }

            // 横軸は下端
            yScaleList[0][1] = lineWidthAxis;

            break;

        default:
            $.writeln ( 'scaleTypeが正しくありません' );
    }
          
    // 水平方向の線の描画
    for (i=0; i<yScaleList.length; i++){
        // 目盛線の描画
        var y = yScaleList[i][0];
        var lineWidth = yScaleList[i][1]
        var lineStart = [0, y];
        var lineEnd = [widthGraph, y];
        var ptlist = [lineStart, lineEnd];
        drawLine(ptlist, colorScale, lineWidth);
        // 目盛数字の描画
        var text = yScaleList[i][2];
        var txtObj = putText(text, [-fontSizeScale*0.5, y-fontSizeScale*0.5], fontScale, fontSizeScale,  colorTextScale);
        txtObj.textRange.justification = Justification.RIGHT;
    }

    // 垂直方向の線
    // 縦軸
    drawLine([[0, 0], [0, -heightGraph]], colorScale, lineWidthAxis);
    txtStart = putText('START', [0, -heightGraph - fontSizeScale*1.5], fontScale, fontSizeScale, colorTextScale);
    txtStart.textRange.justification = Justification.CENTER;
    
    // 縦軸の目盛り線
    var xScale = fps * 60;
    var minute = Math.floor(lengthMatch / xScale);

    for (i=1; i<=minute; i++){
        var x = i * xScale / lengthMatch * widthGraph;
        var ptlist = [[x, 0], [x, -heightGraph]];
        drawLine(ptlist, colorScale, lineWidthScale);
        var text = i + ':00'
        txtObj = putText(text, [x, -heightGraph - fontSizeScale*1.5], fontScale, fontSizeScale, colorTextScale);
        txtObj.textRange.justification = Justification.CENTER;
    }

    drawLine([[widthGraph, 0], [widthGraph, -heightGraph]], colorScale, 1);
    txtObj = putText('FINISH', [widthGraph, -heightGraph - fontSizeScale*1.5], fontScale, fontSizeScale, colorTextScale);
    txtObj.textRange.justification = Justification.CENTER;
    
}


function makeLinePointList(countLineList, yScaleMax) {
    // グラフ線の座標リストを作る
    var ptlist = [[0, -1 * heightGraph]];
    var key = 1;    

    for (i=0; i<lengthMatch; i++){
        var x = i / lengthMatch * widthGraph;
        var y = (1 - countLineList[i] / yScaleMax) * heightGraph * (-1); 

        var yPre = ptlist[ptlist.length-1][1]; 
        
        if (y == yPre){
            if (key == 0){
                ptlist[ptlist.length-1] = [x, y];
            }else{
                ptlist.push([x, y]);
            }

            key = 0;

        }else{
            ptlist.push([x, y]);
            key = 1;
        }
    }

    return ptlist;
}


////////////////////////////////////////////////////////////////////////////////////////////
/* グラフの設定を選ぶダイアログを表示する */
function makeDialogSetting(rule){
    ruleList = ["ナワバリバトル", "ガチエリア", "ガチヤグラ", "ガチホコバトル", "ガチアサリ"];

    // ウインドウ作成
    winObj = new Window("dialog", "グラフを描画する", [0, 0, 300, 400]);

    ruleText = winObj.add("statictext", [20, 20, 280, 40], "ファイルが読み込まれていません");

    ddnBack = winObj.add("panel", [10, 50, 290, 345], "dd");
    ddnObj = winObj.add ('dropdownlist', [20, 50, 180, 70], ruleList);
    groupSetting = winObj.add("group", [20, 80, 280, 325]);

    switch (rule) {
        default:
            ruleJPN = ruleList[0];
            ddnObj.selection = 0;
            break;
        case "zones":
            ruleJPN = ruleList[1];
            ddnObj.selection = 1;
            break;
        case "tower":
            ruleJPN = ruleList[2];
            ddnObj.selection = 2;
            break;            
        case "rain":
            ruleJPN = ruleList[3];
            ddnObj.selection = 3;
            break;
        case "clam":
            ruleJPN = ruleList[4];
            ddnObj.selection = 4;
            break;
    }

    setSetting();
    controlEnabled();
    ruleText.text = "ファイルから読み込んだルール : " + ruleJPN;
    
    okBtn = winObj.add("button", [40, 365, 140, 390], "OK", {name:'ok'});
    canBtn = winObj.add("button", [160, 365, 260, 390], "キャンセル", {name:'cancel'});
    ddnObj.onChange = setSetting;
    checkLine1.onClick = controlEnabled;
    checkLine2.onClick = controlEnabled;
    checkBack1.onClick = controlEnabled; 

    //キャンセルボタンがクリックされたとき
    canBtn.onClick = function () { 
        winObj.close();
    };

    //OKボタンがクリックされたとき
    okBtn.onClick = function () {
        winObj.close();
        drawGraph();
    };

    // ダイアログ表示
    winObj.center();
    winObj.show();
}


/* ダイアログの設定欄をつくる */
function setSetting (){
    winObj.remove(groupSetting);
    groupSetting = winObj.add("group", [20, 80, 280, 325]);

    switch (ddnObj.selection.index) {
        case 0:
            setSettingTurf();
            break;
        case 1:
            setSettingZones();
            break;
        case 2:
            setSettingTower();
            break;
        case 3:
            setSettingRain();
            break;
        case 4:
            setSettingClam();
            break;
    }
}


function controlEnabled(){
    if ( checkLine1.value ){
        checkLine1A.enabled = true;
        checkLine1B.enabled = true;
    }else{
        checkLine1A.enabled = false;
        checkLine1B.enabled = false;
    }

    if ( checkLine2.value ){
        checkLine2A.enabled = true;
        checkLine2B.enabled = true;
    }else{
        checkLine2A.enabled = false;
        checkLine2B.enabled = false;
    }

    if ( checkBack1.value ){
        checkBack1A.enabled = true;
        checkBack1B.enabled = true;
    }else{
        checkBack1A.enabled = false;
        checkBack1B.enabled = false;
    }
}

/* 各ルールの設定欄を作る */
function setSettingTurf(){
    groupSetting.add("statictext", [0, 0, 260, 20], "描画できるグラフがありません");
    groupLine1 = groupSetting.add("group", [30, 55, 250, 75]);
}

function setSettingZones(){
    // 折れ線グラフの設定
    groupLine = groupSetting.add("group", [0, 0, 260, 85]);
    panelLine = groupLine.add("panel", [0, 0, 260, 85], "折れ線グラフ");
    checkLine1 = groupLine.add("checkbox", [10, 30, 250, 50], "カウント進行");
    checkLine1.value = true;

    groupLine1 = groupLine.add("group", [30, 55, 250, 75]);
    checkLine1A = groupLine1.add("checkbox", [0, 0, 100, 20], "アルファ");
    checkLine1B = groupLine1.add("checkbox", [100, 0, 220, 20], "ブラボー");
    checkLine1A.value = true;
    checkLine1B.value = true;

    // 背景の設定
    groupBack = groupSetting.add("group", [0, 105, 260, 220]);
    panelBack = groupBack.add("panel", [0, 0, 260, 115], "背景");
    checkBack1 = groupBack.add("checkbox", [10, 30, 250, 50], "ガチエリア確保状況を背景に表示する");
    checkBack1.value = true;

    groupBack1 = groupBack.add("group", [30, 55, 250, 75]);
    checkBack1A = groupBack1.add("checkbox", [0, 0, 100, 20], "アルファ");
    checkBack1B = groupBack1.add("checkbox", [100, 0, 220, 20], "ブラボー");
    checkBack1A.value = true;
    checkBack1B.value = true;

    checkBack2 = groupBack.add("checkbox", [10, 85, 250, 105], "各エリアの塗り状況を背景に表示する");
    checkBack2.value = true;
}

function setSettingTower(){
    // 折れ線グラフの設定
    groupLine = groupSetting.add("group", [0, 0, 260, 115]);
    panelLine = groupLine.add("panel", [0, 0, 260, 115], "折れ線グラフ");
    checkLine1 = groupLine.add("radiobutton", [10, 30, 200, 50], "カウント進行");
    checkLine2 = groupLine.add("radiobutton", [10, 85, 200, 105], "ガチヤグラの位置");
    checkLine1.value = true;

    groupLine1 = groupLine.add("group", [30, 55, 200, 75]);
    checkLine1A = groupLine1.add("checkbox", [0, 0, 100, 20], "アルファ");
    checkLine1B = groupLine1.add("checkbox", [100, 0, 220, 20], "ブラボー");
    checkLine1A.value = true;
    checkLine1B.value = true;

    // 背景の設定
    groupBack = groupSetting.add("group", [0, 135, 260, 220]);
    panelBack = groupBack.add("panel", [0, 0, 260, 85], "背景");
    checkBack1 = groupBack.add("checkbox", [10, 30, 250, 50], "ガチヤグラ確保状況を背景に表示する");
    checkBack1.value = true;

    groupBack1 = groupBack.add("group", [30, 55, 200, 75]);
    checkBack1A = groupBack1.add("checkbox", [0, 0, 100, 20], "アルファ");
    checkBack1B = groupBack1.add("checkbox", [100, 0, 220, 20], "ブラボー");
    checkBack1A.value = true;
    checkBack1B.value = true;
}

function setSettingRain(){
    // 折れ線グラフの設定
    groupLine = groupSetting.add("group", [0, 0, 260, 115]);
    panelLine = groupLine.add("panel", [0, 0, 260, 115], "折れ線グラフ");
    checkLine1 = groupLine.add("radiobutton", [10, 30, 200, 50], "カウント進行");
    checkLine2 = groupLine.add("radiobutton", [10, 85, 200, 105], "ガチホコの位置");
    checkLine1.value = true;

    groupLine1 = groupLine.add("group", [30, 55, 200, 75]);
    checkLine1A = groupLine1.add("checkbox", [0, 0, 100, 20], "アルファ");
    checkLine1B = groupLine1.add("checkbox", [100, 0, 220, 20], "ブラボー");
    checkLine1A.value = true;
    checkLine1B.value = true;

    // 背景の設定
    groupBack = groupSetting.add("group", [0, 135, 260, 220]);
    panelBack = groupBack.add("panel", [0, 0, 260, 85], "背景");
    checkBack1 = groupBack.add("checkbox", [10, 30, 250, 50], "ガチホコ確保状況を背景に表示する");
    checkBack1.value = true;

    groupBack1 = groupBack.add("group", [30, 55, 200, 75]);
    checkBack1A = groupBack1.add("checkbox", [0, 0, 100, 20], "アルファ");
    checkBack1B = groupBack1.add("checkbox", [100, 0, 220, 20], "ブラボー");
    checkBack1A.value = true;
    checkBack1B.value = true;
}

function setSettingClam(){
    // 折れ線グラフの設定
    groupLine = groupSetting.add("group", [0, 0, 260, 140]);
    panelLine = groupLine.add("panel", [0, 0, 260, 140], "折れ線グラフ");
    checkLine1 = groupLine.add("radiobutton", [10, 30, 200, 50], "カウント進行");
    checkLine2 = groupLine.add("radiobutton", [10, 85, 200, 105], "アサリの保有数");
    checkLine1.value = true;

    groupLine1 = groupLine.add("group", [30, 55, 200, 75]);
    checkLine1A = groupLine1.add("checkbox", [0, 0, 100, 20], "アルファ");
    checkLine1B = groupLine1.add("checkbox", [100, 0, 220, 20], "ブラボー");
    checkLine1A.value = true;
    checkLine1B.value = true;
    
    groupLine2 = groupLine.add("group", [30, 110, 200, 130]);
    checkLine2A = groupLine2.add("checkbox", [0, 0, 100, 20], "アルファ");
    checkLine2B = groupLine2.add("checkbox", [100, 0, 220, 20], "ブラボー");
    checkLine2A.value = true;
    checkLine2B.value = true;

    // 背景の設定
    groupBack = groupSetting.add("group", [0, 160, 260, 245]);
    panelBack = groupBack.add("panel", [0, 0, 260, 85], "背景");
    checkBack1 = groupBack.add("checkbox", [10, 30, 250, 50], "チャンスタイムを背景に表示する");
    checkBack1.value = true;

    groupBack1 = groupBack.add("group", [30, 55, 250, 75]);
    checkBack1A = groupBack1.add("checkbox", [0, 0, 100, 20], "アルファ");
    checkBack1B = groupBack1.add("checkbox", [100, 0, 220, 20], "ブラボー");
    checkBack1A.value = true;
    checkBack1B.value = true;
}


function drawGraph(){

}



////////// 汎用関数 ////////////////////////////////////////////////////
/* 外部CSVファイル読み込み */
// filePathはオブジェクトを入れても問題なく動く
function readCSV(filePath){
	var fileObj = new File(filePath);   // File()はオブジェクトを入れたらそのまま返すらしい
	if (fileObj.exists){
        var flag = fileObj.open("r","","");
        
        if (flag){
            var madeList = [];
            while ( !fileObj.eof ){
                var row = fileObj.readln();
                var rowSplited = row.split(",");
                madeList.push(rowSplited);
            }
            return madeList; 
        }
    }
}

/* 配列を縦に切り出す */
function verticalSlice(inputArray, index) {
    var returnArray = [];
    for (i=0; i<inputArray.length; i++){
        returnArray.push(inputArray[i][index]);
    }
    return returnArray;
}


////////// Illustrator用の関数 ////////////////////////////////////////////////////
/* 配列を色情報にする */
function setColor(color){
    var tmpColor = new RGBColor();
    tmpColor.red = color[0];
    tmpColor.green = color[1];
    tmpColor.blue = color[2];
    return tmpColor;
}

/* パスを配置する */
function drawLine(ptlist, color, widthGraph){
    // 線オブジェクトを生成
	linObj = app.activeDocument.pathItems.add();
	// 塗りつぶしなし
	linObj.filled = false;			
	// 線の色設定
	linObj.strokeColor = setColor(color);	
	// 座標を設定
    linObj.setEntirePath(ptlist);
    // 線の太さを指定
    linObj.strokeWidth = widthGraph;
    // 線の角の形状
    linObj.strokeCap  = StrokeCap.ROUNDENDCAP;
    linObj.strokeJoin = StrokeJoin.ROUNDENDJOIN;

    // グラフの左上座標まで移動
    linObj.translate(pointOrigin[0], pointOrigin[1]);

    redraw();
    return linObj;
}

/* 矩形パスを配置する */
function drawRectangle(TL, BR, colorLine, colorFill){
    // 高さと幅
    widthRect = BR[0] - TL[0];  
    heightRect = BR[1] - TL[1];
    // 矩形オブジェクトを生成
    rectObj = app.activeDocument.pathItems.rectangle(TL[1], TL[0], widthRect, -heightRect);

    // 線の色
    if (colorLine=='false'){
        rectObj.stroked = false;
    }else{
        rectObj.strokeColor = setColor(colorLine);	
        // 線の角の形状
        rectObj.strokeCap   = StrokeCap.ROUNDENDCAP;
        rectObj.strokeJoin  = StrokeJoin.ROUNDENDJOIN;
    }

    // 塗りつぶしの色
    if (colorFill=='false'){
        rectObj.filled = false;
    }else{
        rectObj.fillColor = setColor(colorFill);	
        // 透明度
        rectObj.opacity = 50;
    }
    
    // 最背面に移動
    rectObj.zOrder(ZOrderMethod.SENDTOBACK);

    // グラフの左上座標まで移動
    rectObj.translate(pointOrigin[0], pointOrigin[1]);

    redraw();
    return rectObj;
}

/* テキストを配置する */
function putText(text, point, font, fontSize, color){
    var txtObj = app.activeDocument.textFrames.add();
    // 文字内容
    txtObj.contents = text;
    // 文字位置
    txtObj.translate(point[0], point[1]);
    // フォント検索 -> 見つかれば変更
    try{
        getFont = app.textFonts.getByName(font);
        txtObj.textRange.textFont = getFont;
    } 	
    catch(e)
	{
		$.writeln ( "error linObj:" + e.linObj + " - " + e.message );
    }  
    // 文字サイズ
    txtObj.textRange.size = fontSize;
    // 文字色
    txtObj.textRange.characterAttributes.fillColor = setColor(color);

    // 文字ヅメ
    txtObj.textRange.kerning = -50;

    // グラフの左上座標まで移動
    txtObj.translate(pointOrigin[0], pointOrigin[1]);

    redraw();
    return txtObj;
}


////////////////////////////////////////////////////////////////////////
// メッセージ
function makeMessage( msgType ) {
    switch( msgType ){
        case "pref" : mA = [
                "■ハガキ宛名支援・設定用テキスト■",
                "rowSplitedFileName:rowSplited.txt	←読み込むデータのファイル名（拡張子つき・半角英数字）",
                "sheetNum:1	←印刷する枚数" ] ; 
                break ;

        case "noFile":
            msg = "ファイルが指定されませんでした。\nスクリプトを終了します。";
            break;

        case "err1":
            msg = "~count.csvもしくは~status.csvのファイルを指定してください";
            break;

        case "err2":
            msg = "countもしくはstatusファイルが見つかりません";
            break;

        case "err3":
            msg = "CSVファイルが読み込めませんでした。";
            break;

        case "endScript":
            msg = "スクリプトを終了します。";

        default:
            msg = "不明なエラー";
    } ;
    return msg;
}
