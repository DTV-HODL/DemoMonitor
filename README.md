Demo BTC Transaction Monitor

This app is intended for users that incorporate a standard 12 or 24 word seed phrase wallet ("honeypot") with a minimal amount of BTC and a passphrase wallet ("main stack") utilizing the same 12 or 24 word seed phrase.  The app will monitor the honeypot and if funds are swept will notify the user so that they can sweep the passphrased funds prior to the attacker gaining access to the funds.

There are currently web sites that will monitor transactions but these sites are public and have the ability to associate transactions with the web site users via IP.

This app will monitor a list of transaction outputs.  It checks for a new block at a specified interval (set in config).  When a new block is discovered the app will scan the list of transaction outputs that the user has provided in the config file.  The app will check the current block as well as the mempool for each transaction output.

If a spent transaction output is discovered the app wil notify the user via the UI as well as sending a SMS text message to a number provided by the user in the config.

The text message notifies the user that a transaction was spent and provides the trans_number (as set in the config file) along with a descriptive name of the wallet that the user also provides in the config file.

This app currently runs on MacOS and requires a local bitcoin core implementation to be running on the same machine.

I have not incorporated any error handling at this commit.

My intention is to create a new GUI that is browser based (webui) so that the app can eventually be packaged in a docker and run on an Umbrel bitcoin node.  

By running on a private bitcoin node all the users transaction information is kept private and never transmitted over the web.