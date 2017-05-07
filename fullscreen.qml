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
        text: qsTr("Start")
        anchors.verticalCenter: startStopSpacer.verticalCenter
        anchors.horizontalCenter: startStopSpacer.horizontalCenter
        isDefault: true
    }

    Connections {
        target: startStopButton
        onClicked: startRecording()
    }

    signal startRecording()

    function stateRecording(){
        state = "ScanningState"
    }

    function stateReady(){
        state = "ResultState"
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
        x: 233
        y: 444
        text: qsTr("1")
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        anchors.right: button1.left
        anchors.rightMargin: 1
        antialiasing: true
    }

    Button {
        id: button1
        x: 318
        y: 444
        text: qsTr("2")
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        anchors.horizontalCenter: parent.horizontalCenter
    }

    Button {
        id: button2
        y: 444
        text: qsTr("3")
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        anchors.left: button1.right
        anchors.leftMargin: 0
    }

    Flow {
    }

    Connections {
        target: button
        onClicked: { fullscreenItem.state = "" }
    }

    Connections {
        target: button1
        onClicked: { fullscreenItem.state = "ScanningState" }
    }

    Connections {
        target: button2
        onClicked: { fullscreenItem.state = "RestultState" }
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
