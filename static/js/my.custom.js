var mW = 400;
    var mH = 400;
    var mData = [
        ['指标1', 21],
        ['指标2', 56],
        ['指标3', 46],
        ['指标4', 50],
        ['指标5', 80]
    ];
    var mCount = mData.length; //边数
    var mCenter = mW /2; //中心点
    var mRadius = mCenter - 50; //半径(减去的值用于给绘制的文本留空间)
    var mAngle = Math.PI * 2 / mCount; //角度
    var mCtx = null;
    var mColorPolygon = '#B8B8B8'; //多边形颜色
    var mColorLines = '#B8B8B8'; //顶点连线颜色
    var mColorText = '#000000';

    //初始化
    (function(){
        var canvas = document.createElement('canvas');
        document.body.appendChild(canvas);
        canvas.height = mH;
        canvas.width = mW;
        mCtx = canvas.getContext('2d');
        drawPolygon(mCtx);
        drawLines(mCtx);
        drawRegion(mCtx);
        drawText(mCtx);
        drawCircle(mCtx);
        drawLines1(mCtx)
    })();

    // 绘制多边形边
    function drawPolygon(ctx){
        ctx.save();

        ctx.strokeStyle = mColorPolygon;
        var r = mRadius/ mCount; //单位半径
        // var r = mRadius/ (mCount-2); //单位半径  画三个五边形
        //画5个圈
        for(var i = 0; i < mCount; i ++){
         // for(var i = 0; i < mCount-2; i ++){ // 画三个五边形
            ctx.beginPath();
            var currR = r * ( i + 1); //当前半径
            //画5条边
            for(var j = 0; j < mCount; j ++){
                var x = mCenter + currR * Math.cos(mAngle * j);
                var y = mCenter + currR * Math.sin(mAngle * j);

                ctx.lineTo(x, y);
            }
            ctx.closePath()
            ctx.stroke();
        }

        ctx.restore();
    }

    //顶点连线
    function drawLines(ctx){
        ctx.save();

        ctx.beginPath();
        ctx.strokeStyle = mColorLines;

        for(var i = 0; i < mCount; i ++){
            var x = mCenter + mRadius * Math.cos(mAngle * i);
            var y = mCenter + mRadius * Math.sin(mAngle * i);

            ctx.moveTo(mCenter, mCenter);
            ctx.lineTo(x, y);
        }

        ctx.stroke();

        ctx.restore();
    }

    //数据点之间的连线
    function drawLines1(ctx){
        ctx.save();
        ctx.beginPath();
        var count = 0;
        for(var i = 0; i < mCount; i ++){
            var x = mCenter + mRadius * Math.cos(mAngle * i) * mData[i][1] / 100;
            var y = mCenter + mRadius * Math.sin(mAngle * i) * mData[i][1] / 100;
            count = i + 1;
            if (count < mCount) {
                var x1 = mCenter + mRadius * Math.cos(mAngle * (i+1)) * mData[i+1][1] / 100;
                var y1 = mCenter + mRadius * Math.sin(mAngle * (i+1)) * mData[i+1][1] / 100;
            }else{
                var x1 = mCenter + mRadius * Math.cos(mAngle * 0) * mData[0][1] / 100;
                var y1 = mCenter + mRadius * Math.sin(mAngle * 0) * mData[0][1] / 100;
            }
            ctx.moveTo(x, y);
            ctx.lineTo(x1, y1);
            ctx.lineWidth = 2;          //设置线宽状态
            ctx.strokeStyle = '#1478FA';  //设置线的颜色状态
        }
        ctx.stroke();

        ctx.restore();
    }
    //绘制文本
    function drawText(ctx){
        ctx.save();

        var fontSize = mCenter / 12;
        ctx.font = fontSize + 'px Microsoft Yahei';
        ctx.fillStyle = mColorText;

        for(var i = 0; i < mCount; i ++){
            var x = mCenter + mRadius * Math.cos(mAngle * i);
            var y = mCenter + mRadius * Math.sin(mAngle * i);

            if( mAngle * i >= 0 && mAngle * i <= Math.PI / 2 ){
                ctx.fillText(mData[i][0], x, y + fontSize);
            }else if(mAngle * i > Math.PI / 2 && mAngle * i <= Math.PI){
                ctx.fillText(mData[i][0], x - ctx.measureText(mData[i][0]).width, y + fontSize);
            }else if(mAngle * i > Math.PI && mAngle * i <= Math.PI * 3 / 2){
                ctx.fillText(mData[i][0], x - ctx.measureText(mData[i][0]).width, y);
            }else{
                ctx.fillText(mData[i][0], x, y);
            }

        }
        //中心绘制文字
        ctx.font="bold 36px Arial"
        ctx.fillStyle='#1478FA'
        ctx.fillText("75",mCenter-18,mCenter+16);

        ctx.restore();
    }

    //绘制数据区域
    function drawRegion(ctx){
        ctx.save();

        ctx.beginPath();
        for(var i = 0; i < mCount; i ++){
            var x = mCenter + mRadius * Math.cos(mAngle * i) * mData[i][1] / 100;
            var y = mCenter + mRadius * Math.sin(mAngle * i) * mData[i][1] / 100;

            ctx.lineTo(x, y);
        }
        ctx.closePath();
        ctx.fillStyle = 'rgba(255, 0, 0, 0.5)';
        ctx.fill();

        ctx.restore();
    }

    //画点
    function drawCircle(ctx){
        ctx.save();

        var r = mCenter / 50;
        for(var i = 0; i < mCount; i ++){
            var x = mCenter + mRadius * Math.cos(mAngle * i) * mData[i][1] / 100;
            var y = mCenter + mRadius * Math.sin(mAngle * i) * mData[i][1] / 100;

            ctx.beginPath();
            ctx.arc(x, y, r, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(20, 120, 250, 0.8)';
            ctx.fill();
        }

        ctx.restore();
    }