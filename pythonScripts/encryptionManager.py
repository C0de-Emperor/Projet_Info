encryptingList=[chr(k) for k in range(33, 383) if k<=126 or k>=161]

# maximum encryting depth is 999, otherwise maximum recursion depth is exceeded
def caesarBoosted(word, key, encryptingDepth, isReversed=False):
    newWord=""
    i=0
    for k in word:
        newCharacterIndex=encryptingList.index(k)
        if not isReversed: newCharacterIndex+=encryptingList.index(key[i])
        else: newCharacterIndex+=encryptingList.index(key[len(key)-i-1])
        while newCharacterIndex>=len(encryptingList): newCharacterIndex-=len(encryptingList)
        newWord+=encryptingList[newCharacterIndex]
        i+=1
        if i>=len(key): i=0
    
    if encryptingDepth<=1:
        return newWord
    else:
        return caesarBoosted(newWord, key, encryptingDepth-1, isReversed)

def decryptCaesarBoosted(word, key, decryptingDepth, isReversed=False):
    newWord=""
    i=0
    for k in word:
        newCharacterIndex=encryptingList.index(k)
        if not isReversed: newCharacterIndex-=encryptingList.index(key[i])
        else: newCharacterIndex-=encryptingList.index(key[len(key)-i-1])
        while newCharacterIndex<0: newCharacterIndex+=len(encryptingList)
        newWord+=encryptingList[newCharacterIndex]
        i+=1
        if i>=len(key): i=0
    
    if decryptingDepth<=1:
        return newWord
    else:
        return decryptCaesarBoosted(newWord, key, decryptingDepth-1, isReversed)

print(caesarBoosted("bonjour", "bonjour", 999))
print(decryptCaesarBoosted(caesarBoosted("bonjour", "bonjour", 999), "bonjour", 999))
