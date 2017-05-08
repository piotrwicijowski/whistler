import QtQuick 2.5
import QtQuick.Controls 1.4

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
        width: fullscreenItem.width/8
        height: fullscreenItem.height/12
        text: qsTr("Start")
        anchors.verticalCenter: startStopSpacer.verticalCenter
        anchors.horizontalCenter: startStopSpacer.horizontalCenter
        isDefault: true

    }

    Shortcut {
        sequence: "Space"
        onActivated: startRecording()
        context: Qt.ApplicationShortcut
    }

    Shortcut {
        sequence: "Escape"
        onActivated: closeWindow()
        context: Qt.ApplicationShortcut
    }

    Connections {
        target: startStopButton
        onClicked: startRecording()
    }

    signal startRecording()

    signal closeWindow()

    function stateRecording(){
        state = "ScanningState"
    }

    function stateReady(resultString){
        state = "ResultState"
        resultsText.text = resultString
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
            height: parent.height*4/5
            opacity: 1
            anchors.leftMargin: (resultsItem.height-resultsImage.height)/2
//            anchors.leftMargin: (resultsItem.height-resultsImage.height)
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            source: "image.jpg"
        }

        Text {
            id: resultsText
            y: 68
            height: 64
            color: "#e6e6e6"
            text: qsTr("Text")
            anchors.leftMargin: resultsImage.anchors.leftMargin/2
            anchors.left: resultsImage.right
            anchors.rightMargin: resultsImage.anchors.leftMargin
            anchors.right: parent.right
            anchors.verticalCenter: resultsImage.verticalCenter
            font.pixelSize: 23
            verticalAlignment: Text.AlignVCenter
        }
    }

    Button {
        id: button
        x: 556
        width: Math.min(fullscreenItem.width/16,fullscreenItem.height/16)
        height: width
        text: qsTr("X")
        anchors.top: parent.top
        anchors.topMargin: 0
        anchors.right: parent.right
        anchors.rightMargin: 0
        antialiasing: true
    }

    Flow {
    }

    Connections {
        target: button
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
//            PropertyChanges {
//                target: resultsImage
//                anchors.leftMargin: (resultsItem.height-resultsImage.height)/2
//            }
            PropertyChanges {
                target:startStopButton
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
