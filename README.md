# Kanshin Export Tool

関心空間から公開されているキーワード情報をダウンロードするツールです。

## 使い方

Python3が必要です。Homebrewで入れるのが簡単です。
```
brew install python3
```

Homebrewのインストール方法は、
```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)”
```
詳しくは http://brew.sh/index_ja.html


```
pip3 install --upgrade -r requirements.txt
python3 fetch.py `user_id`
```

## 注意点
まだ一部のキーワードしかダウンロードしません。内容に問題がなくなったタイミングで全キーワードを対象にします。

本文内に含まれるURLが不完全です

## LICENSE

The MIT License (MIT)
