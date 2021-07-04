# WEBサーバーデータバックアップ

## 作成経緯
多重SSH接続(SSH+SFTP)を使用してWEBサーバーの特定ディレクトリをバックアップする必要があったのでスクリプト化。
私用に作成したので汎用性はありません。

## python依存ライブラリ
paramiko
http://www.paramiko.org/

sshtunnel
https://sshtunnel.readthedocs.io/en/latest/