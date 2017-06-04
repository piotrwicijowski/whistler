import QtQuick 2.5
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtMultimedia 5.8

Rectangle {
    id: fullscreenItem
    width: 640
    height: 480
    color: "#0d0d0d"
    Item {
        id: startStopSpacer
        anchors.right: parent.right
        anchors.rightMargin: 0
        anchors.left: parent.left
        anchors.leftMargin: 0
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        anchors.top: parent.top
        anchors.topMargin: 0
    }

    Button {
        id: startStopButton
        property real hoverResize : 0
        property real progress : 0
        onHoveredChanged: hovered ? state = "hovered" : state = "idle"
        width: Math.min(fullscreenItem.width/4,fullscreenItem.height/4)
        height: width
        text: qsTr("Start")

        visible: true
        anchors.verticalCenter: startStopSpacer.verticalCenter
        anchors.horizontalCenter: startStopSpacer.horizontalCenter
        isDefault: true
        states: [
            State {
                name: "hovered"
                PropertyChanges {
                    target: startStopButton
                    hoverResize: 10.0
                }
            },
            State {
                name: "idle"
                PropertyChanges {
                    target: startStopButton
                    hoverResize: 0.0
                }
            }
        ]
        transitions: Transition {

            PropertyAnimation {
                target: startStopButton
                properties: "hoverResize"
                duration: 100
                easing.type: Easing.InOutQuad
            }

        }
        style: ButtonStyle {
            background:
                Item{
                id: startStopButtonBackgroundItem
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
                width: startStopButton.width + startStopButton.hoverResize
                height: startStopButton.height + startStopButton.hoverResize
                Rectangle {
                    property real strokeWidth: startStopButton.activeFocus ? 4 : 2
                    id: startStopButtonCircle
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: parent.width - 2*progressArc.strokeWidth + strokeWidth
                    height: parent.height - 2*progressArc.strokeWidth + strokeWidth
                    color: "#00000000"
                    radius: width*0.5
                    border.width: strokeWidth
                    z: 0
                    border.color: "#e6e6e6"
                }
                Canvas {
                    id: progressArc
                    anchors.fill: parent
                    antialiasing: true

                    property color progressColor: "lightblue"

                    property real strokeWidth: 6
                    property real centerWidth: width / 2
                    property real centerHeight: height / 2
                    property real radius: Math.min(centerWidth - strokeWidth, centerHeight - strokeWidth)

                    property real minimumValue: 0
                    property real maximumValue: 100
                    property real currentValue: startStopButton.progress

                    // this is the angle that splits the circle in two arcs
                    // first arc is drawn from 0 radians to angle radians
                    // second arc is angle radians to 2*PI radians
                    property real angle: (currentValue - minimumValue) / (maximumValue - minimumValue) * 2 * Math.PI

                    // we want both circle to start / end at 12 o'clock
                    // without this offset we would start / end at 9 o'clock
                    property real angleOffset: -Math.PI / 2

                    onProgressColorChanged: requestPaint()
                    onMinimumValueChanged: requestPaint()
                    onMaximumValueChanged: requestPaint()
                    onCurrentValueChanged: requestPaint()

                    onPaint: {
                        var ctx = getContext("2d");
                        ctx.save();

                        ctx.clearRect(0, 0, progressArc.width, progressArc.height);

                        ctx.beginPath();
                        ctx.lineWidth = progressArc.strokeWidth;
                        ctx.strokeStyle = progressArc.progressColor;
                        ctx.arc(progressArc.centerWidth,
                                progressArc.centerHeight,
                                progressArc.radius,
                                progressArc.angleOffset,
                                progressArc.angleOffset + progressArc.angle);
                        ctx.stroke();

                        ctx.restore();
                    }
                }
            }

            label: Text {
                renderType: Text.NativeRendering
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                //font.family: "Helvetica"
                font.pointSize: 14
                color: "#e6e6e6"
                text: control.text
            }
        }
    }

    Shortcut {
        sequence: "Space"
        onActivated: toggleRecording()
        context: Qt.ApplicationShortcut
    }

    Shortcut {
        sequence: "Escape"
        onActivated: closeWindow()
        context: Qt.ApplicationShortcut
    }

    Connections {
        target: playResultsButton
        onClicked: playAudio()
    }

    // Connections {
    //     target: playVideoButton
    //     onClicked: playVideo()
    // }

    Audio {
        id: resultsAudio
    }

    function playVideo(){
        // if(resultsVideo.playbackState == MediaPlayer.PlayingState)
        //     resultsVideo.pause()
        // else if(resultsVideo.playbackState == MediaPlayer.PausedState)
        //     resultsVideo.play()
        // else if(resultsVideo.playbackState == MediaPlayer.StoppedState)
            resultsVideo.play()
    }

    function playAudio(){
        if(resultsAudio.playbackState == Audio.PlayingState)
            resultsAudio.pause()
        else if(resultsAudio.playbackState == Audio.PausedState)
            resultsAudio.play()
        else if(resultsAudio.playbackState == Audio.StoppedState)
            resultsAudio.play()
    }

    Connections {
        target: startStopButton
        onClicked: toggleRecording()
    }
    function toggleRecording(){
        if(state=="ScanningState"){
            stopRecording()
        }else{
            resultsAudio.stop()
            startRecording()
        }
    }
    signal startRecording()

    signal stopRecording()

    signal closeWindow()

    function disableAutoPlayback(disabled){
        disabled = typeof disabled !== 'undefined' ? disabled : true
        enableAutoPlayback(!disabled)
    }

    function enableAutoPlayback(enabled){
        enabled = typeof enabled !== 'undefined' ? enabled : true
        playResultsButton.autoEnabled = enabled
    }

    function disablePlayback(disabled){
        disabled = typeof disabled !== 'undefined' ? disabled : true
        enablePlayback(!disabled)
    }

    function enablePlayback(enabled){
        enabled = typeof enabled !== 'undefined' ? enabled : true
        playResultsButton.enabled = enabled
    }

    function stateRecording(){
        state = "ScanningState"
    }

    function stateReady(resultString, imagePath, audioPath, videoPath){
        state = "ResultState"
        resultsText.text = resultString
        resultsImage.source = imagePath
        resultsAudio.source = audioPath
        resultsVideo.source = videoPath
        if(playResultsButton.autoEnabled)
            resultsAudio.play()
    }

    function setProgress(progress){
        startStopButton.progress = progress
    }

    Item {
        id: resultsItem
        x: 93
        width: parent.width*10/12
        height: parent.height/2.5
        anchors.topMargin: 60
        anchors.horizontalCenterOffset: 0
        anchors.top: parent.top
        opacity: 0
        anchors.horizontalCenter: parent.horizontalCenter

        Image {
            id: resultsImage
            y: 57
            width: height
            fillMode: Image.PreserveAspectFit
            height: parent.height*4/5
            opacity: 1
            anchors.leftMargin: (resultsItem.height-resultsImage.height)/2
            //anchors.leftMargin: (resultsItem.height-resultsImage.height)
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            source: "image.jpg"
        }

        Video {
            property bool enabled: true
            property bool autoEnabled: true
            id: resultsVideo
            width: height
            height: parent.height*4/5
            fillMode: VideoOutput.PreserveAspectFit
            opacity: 1
            anchors.leftMargin: (resultsItem.height-resultsVideo.height)/2
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            autoPlay: true
            onStopped: play()
            muted: true
            // loops: MediaPlayer.Infinite
        }


        Text {
            id: resultsText
            // y: 68
            height: resultsImage.height
            color: "#e6e6e6"
            text: qsTr("Text")
            clip: true
            anchors.leftMargin: resultsImage.anchors.leftMargin/2
            anchors.left: resultsImage.right
            anchors.rightMargin: resultsImage.anchors.leftMargin
            anchors.right: playResultsButton.visible ? playResultsButton.left : parent.right
            anchors.verticalCenter: resultsImage.verticalCenter
            font.pixelSize: 23
            verticalAlignment: Text.AlignVCenter
        }
        Button {
            id: playResultsButton
            property bool enabled: true
            property bool autoEnabled: true
            property real hoverResize : 0
            property real progress : resultsAudio.position / resultsAudio.duration
            property real ringOpacity : 0.0
            onHoveredChanged: hovered ? state = "hovered" : state = "idle"
            width: height
            height: parent.height*1/4
            text: resultsAudio.playbackState != Audio.PlayingState ? qsTr("►") : qsTr("┃┃")
            visible: resultsAudio.source != "" && enabled

            anchors.rightMargin: (resultsItem.height-playResultsButton.height)/2
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            //isDefault: true
            states: [
                State {
                    name: "hovered"
                    PropertyChanges {
                        target: playResultsButton
                        hoverResize: 10.0
                    }
                    PropertyChanges {
                        target: playResultsButton
                        ringOpacity: 1.0
                    }
                },
                State {
                    name: "idle"
                    PropertyChanges {
                        target: playResultsButton
                        hoverResize: 0.0
                    }
                    PropertyChanges {
                        target: playResultsButton
                        ringOpacity: 0.0
                    }
                }
            ]
            transitions: Transition {

                PropertyAnimation {
                    target: playResultsButton
                    properties: "ringOpacity"
                    duration: 100
                    easing.type: Easing.InOutQuad
                }

                PropertyAnimation {
                    target: playResultsButton
                    properties: "hoverResize"
                    duration: 100
                    easing.type: Easing.InOutQuad
                }

            }
            style: ButtonStyle {
                background:
                    Item{
                    id: playResultButtonBackgroundItem
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: playResultsButton.width + playResultsButton.hoverResize
                    height: playResultsButton.height + playResultsButton.hoverResize
                    Rectangle {
                        property real strokeWidth: playResultsButton.activeFocus ? 4 : 2
                        opacity: playResultsButton.ringOpacity
                        id: playResultButtonCircle
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                        width: parent.width - 2*playProgressArc.strokeWidth + strokeWidth
                        height: parent.height - 2*playProgressArc.strokeWidth + strokeWidth
                        color: "#00000000"
                        radius: width*0.5
                        border.width: strokeWidth
                        z: 0
                        border.color: "#e6e6e6"
                    }
                    Canvas {
                        id: playProgressArc
                        anchors.fill: parent
                        antialiasing: true

                        property color progressColor: "lightblue"

                        property real strokeWidth: 6
                        property real centerWidth: width / 2
                        property real centerHeight: height / 2
                        property real radius: Math.min(centerWidth - strokeWidth, centerHeight - strokeWidth)

                        property real minimumValue: 0
                        property real maximumValue: 1
                        property real currentValue: playResultsButton.progress

                        // this is the angle that splits the circle in two arcs
                        // first arc is drawn from 0 radians to angle radians
                        // second arc is angle radians to 2*PI radians
                        property real angle: (currentValue - minimumValue) / (maximumValue - minimumValue) * 2 * Math.PI

                        // we want both circle to start / end at 12 o'clock
                        // without this offset we would start / end at 9 o'clock
                        property real angleOffset: -Math.PI / 2

                        onProgressColorChanged: requestPaint()
                        onMinimumValueChanged: requestPaint()
                        onMaximumValueChanged: requestPaint()
                        onCurrentValueChanged: requestPaint()

                        onPaint: {
                            var ctx = getContext("2d");
                            ctx.save();

                            ctx.clearRect(0, 0, playProgressArc.width, playProgressArc.height);

                            ctx.beginPath();
                            ctx.lineWidth = playProgressArc.strokeWidth;
                            ctx.strokeStyle = playProgressArc.progressColor;
                            ctx.arc(playProgressArc.centerWidth,
                                    playProgressArc.centerHeight,
                                    playProgressArc.radius,
                                    playProgressArc.angleOffset,
                                    playProgressArc.angleOffset + playProgressArc.angle);
                            ctx.stroke();

                            ctx.restore();
                        }
                    }
                }

                label: Text {
                    renderType: Text.NativeRendering
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    //font.family: "Helvetica"
                    font.pointSize: 24
                    color: "#e6e6e6"
                    text: control.text
                }
            }
        }

    }

    Button {
        id: closeButton
        x: 556
        width: Math.min(fullscreenItem.width/16,fullscreenItem.height/16)
        height: width
        text: qsTr("×")
        anchors.top: parent.top
        anchors.topMargin: 0
        anchors.right: parent.right
        anchors.rightMargin: 0
        antialiasing: true
        style: ButtonStyle {
            background:
                Item{
                id: closeButtonBackgroundItem
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
                width: closeButton.width
                height: closeButton.height
            }

            label: Text {
                renderType: Text.NativeRendering
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                font.pointSize: 14
                color: "#e6e6e6"
                text: control.text
            }
        }
    }

    Flow {
    }

    Connections {
        target: closeButton
        onClicked: closeWindow()
    }

    states: [
        State {
            name: "ScanningState"

            PropertyChanges {
                target: resultsItem
                opacity: 0.0
            }

            PropertyChanges {
                target: startStopButton
                text: qsTr("Skanowanie")
                anchors.verticalCenterOffset: 0
                anchors.horizontalCenterOffset: 0
            }
        },
        State {
            name: "ResultState"

            PropertyChanges {
                target: resultsItem
                opacity: 1.0
            }

            AnchorChanges {
                target: resultsItem
                anchors.verticalCenter: parent.verticalCenter
                anchors.top: undefined
            }

            AnchorChanges {
                target: startStopSpacer
                anchors.top: resultsItem.bottom
            }
            //PropertyChanges {
            //    target: resultsImage
            //    anchors.leftMargin: (resultsItem.height-resultsImage.height)/2
            //}
            PropertyChanges {
                target: startStopButton
                text: qsTr("Start")
            }
        }
    ]
    transitions: Transition {
        // smoothly reanchor myRect and move into new position
        AnchorAnimation {
            targets: resultsItem
            duration: 200
            easing.type: Easing.InOutQuad
        }

        AnchorAnimation {
            targets: startStopSpacer
            duration: 100
            easing.type: Easing.InOutQuad
        }

        PropertyAnimation {
            target: resultsItem
            properties: "opacity"
            duration: 200
            easing.type: Easing.InOutQuad
        }

        PropertyAnimation {
            target: resultsImage
            properties: "anchors.leftMargin"
            duration: 200
            easing.type: Easing.InOutQuad
        }
    }
}
