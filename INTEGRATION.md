# Tokens integration

There are 2 approaches to using tokens layer, first one is to use official tokens node available at [https://tokens.mbc.wiki](https://tokens.mbc.wiki) and second one is to setup your own.

Documentation for api available at [https://tokens.mbc.wiki/docs](https://tokens.mbc.wiki/docs)

In order to setup tokens you need to have synced MicroBitcon node with `txindex=1` and `addressindex=1` enabled.

https://github.com/MicroBitcoinOrg/MicroBitcoin

After that you need to clone Tokens repository and setup dependencies

```bash
git clone https://github.com/MicroBitcoinOrg/Tokens
cd Tokens
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Once setup is done you need to copy and update config with PostgreSQL database and node endpoint

```bash
cp docs/config.example.py config.py
nano config.py
```

Replace `postgres://admin:password@localhost:5432/database` with your database config and update `http://user:password@localhost:6503` with your MicroBitcoin node credentials.

Once this is done you need to sync database. It can be done manually by running

```bash
python3 sync.py
```

or by setting up systemd service (recommended)

```bash
sudo cp docs/sync-tokens.service/ /etc/systemd/system/sync-tokens.service
```

Update service config with proper path to tokens directory

```bash
sudo nano /etc/systemd/system/sync-tokens.service
```

Replace `/home/system_user/tokens` with your path and `system_user` with your username. After that enable and start service

```bash
sudo systemctl enable sync-tokens.service
sudo systemctl start sync-tokens.service
```

Follow same steps to setup `docs/tokens.service`, it will provide tokens backend api at `http://127.0.0.1:5858`.

To verify if everything is working properly make request to GET `http://127.0.0.1:5858/version`, response should look like this

```json
{"version":"0.2.2"}
```

Information about token layer sync can be obtained from GET `/layer/latest`
Tokens list GET `/layer/tokens?page=1`
Token info GET `/layer/token/GOLD`
Token holders GET `/layer/token/GOLD/holders`
Token transfers GET `/layer/token/GOLD/transfers`
Transfer info GET `/layer/tx/6e2b66af6c46f0f351bc9875967dbef3feea58cc534ec3c41bf655d8e37edf5c`
Address info/balances GET `/layer/address/BZBemw9yDYy1p5hsypdBysxaT3UETDPY3m`
Address transfers GET `/layer/address/BZBemw9yDYy1p5hsypdBysxaT3UETDPY3m/transfers`
Address transfers for specific token `/layer/address/BZBemw9yDYy1p5hsypdBysxaT3UETDPY3m/transfers/GOLD`

To build token transfer transaction you need to follow this steps:

Generate transfer message by doing POST `/message/transfer` with following params

```json
{
  "value": 100000000,
  "ticker": "TEST"
}
```

Please take note that value should be specified in satoshis. Basic formula for converting amount to __token__ satoshis looks like this

```
int(amount * 100000000)
```

For example 1 token equals to 100000000 __token__ satoshis.

After making request you will get transfer message which looks like this

```
0185a176c40a00000000000005f5e100a16303a16d01a174a454455354a16cc0
```

Next step is to create raw transaction. For that you can make request to POST `/construct` with following arguments

```json
{
  "marker": 10000,
  "fee": 10000,
  "send_address": "mbc1qfuj6ud4uspcx5vnx0qn565p43tmy6nacqs4808",
  "receive_address": "mbc1qky0r9uec8jjk42h9cr3ry986xtchrl0pakqd7x",
  "payload": "0185a176c40a00000000000005f5e100a16303a16d01a174a454455354a16cc0"
}
```

Marker is the MBC amount which will be send to receiver address in order for token layer to process transfer. Fee is transaction fee. Payload is token transfer message which has been generated above.

Important thing to remember is that MBC only has 4 decimal places, so 1 MBC equals to 10000 satoshis. Fee and makers are specified in MBC satoshis.

For example 1 __MBC__ equals to 10000 satoshis.

In result you will get raw unsigned transaction

```json
{
  "data": "02000000019f03f157a82532664bf1c11d5fe01d29d56a54d06f0470687717585c4123966e0000000000ffffffff0360ea0000000000001600144f25ae36bc80706a326678274d50358af64d4fb80000000000000000226a200185a176c40a00000000000005f5e100a16303a16d01a174a454455354a16cc01027000000000000160014b11e32f3383ca56aaae5c0e23214fa32f171fde100000000"
}
```

Before sending it to the network you must sign it with sender address private key, this can be done trough MicroBitcoin node

```bash
micro-cli signrawtransactionwithkey 02000000019f03f157a82532664bf1c11d5fe01d29d56a54d06f0470687717585c4123966e0000000000ffffffff0360ea0000000000001600144f25ae36bc80706a326678274d50358af64d4fb80000000000000000226a200185a176c40a00000000000005f5e100a16303a16d01a174a454455354a16cc01027000000000000160014b11e32f3383ca56aaae5c0e23214fa32f171fde100000000 '["YOUR_ADDRESS_KEY"]'
```

After signing you will get raw transaction which is ready to be broadcasted to the network

```json
{
  "hex": "020000000001019f03f157a82532664bf1c11d5fe01d29d56a54d06f0470687717585c4123966e0000000000ffffffff0360ea0000000000001600144f25ae36bc80706a326678274d50358af64d4fb80000000000000000226a200185a176c40a00000000000005f5e100a16303a16d01a174a454455354a16cc01027000000000000160014b11e32f3383ca56aaae5c0e23214fa32f171fde10247304402202a1ba451214ebdebf76e1433e93bdb5cf288c0b9c40260bf89ee662d05b9694f02201a83062bfd2280251afe5b1dfc5359d6bbe8816644edfd6e1b612f0a26f5adbc012102b3220bf4474eb0cd1cb044685ee58577803f64fbf94f562c76651d899a7b21cc00000000",
  "complete": true
}
```

It can be done by using `sendrawtransaction` rpc method

```bash
micro-cli sendrawtransaction 020000000001019f03f157a82532664bf1c11d5fe01d29d56a54d06f0470687717585c4123966e0000000000ffffffff0360ea0000000000001600144f25ae36bc80706a326678274d50358af64d4fb80000000000000000226a200185a176c40a00000000000005f5e100a16303a16d01a174a454455354a16cc01027000000000000160014b11e32f3383ca56aaae5c0e23214fa32f171fde10247304402202a1ba451214ebdebf76e1433e93bdb5cf288c0b9c40260bf89ee662d05b9694f02201a83062bfd2280251afe5b1dfc5359d6bbe8816644edfd6e1b612f0a26f5adbc012102b3220bf4474eb0cd1cb044685ee58577803f64fbf94f562c76651d899a7b21cc00000000
```

In return you will receive txid

```
7ad15ebd218bcdf75eefef371b32c60609948d58af543252438be3fe36409c09
```

After transation is processed tokens will be transfered.
