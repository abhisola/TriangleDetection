### Triangle Detection Configuration
## Parameters And Meaning
| Parameter | Meaning | Default Value |
| --------- | ------- | ----- |
| --undistort | Undistorts Images From Corners | -0.00002,0.0000000004,0.00006,0.00006 |
| -b | Boundary Of Detection Box | 0,0,1280,0,1280,720,0,720 |
| --paf | Poly Approximation Factor | 7 |
| --arcmin | Minimum Arc Length | 45 |
| --legmax | Maximum leg length for triangle filtering | 80 |
| --legmin | Minimum leg length for triangle filtering | 10 |
| --legvar | Maximum difference in triangle leg length | 30 |
| --areamin | Minimum Area Of Triangle | 100 |
| --areamax | Maximum Area Of Triangle | 1000 |
| --expected | Expected Number Of Triangles When Shelf Empty | 350 |
> Note : You can use --state for seeing each step as image output
## 1. Overland
### Shelf 0
```sh
--undistort \"-0.00002,0.0000000004,0.00006,0.00006\" -b \"0,0,1280,0,1280,650,0,650\" --paf 7 --arcmin 45 --legmax 80 --legmin 10 --legvar 30 --areamin 100 --areamax 1000 --expected 333
```
### Shelf 1
```sh
--undistort \"-0.00002,0.0000000004,0.00006,0.00006\" -b \"0,0,1280,0,1280,650,0,650\" --paf 7 --arcmin 45 --legmax 80 --legmin 10 --legvar 30 --areamin 100 --areamax 1000 --expected 333
```
### Shelf 2
```sh
--undistort \"-0.00002,0.0000000004,0.00006,0.00006\" -b \"0,0,1280,0,1280,650,0,650\" --paf 7 --arcmin 45 --legmax 80 --legmin 10 --legvar 30 --areamin 100 --areamax 1000 --expected 333
```
### Shelf 3
```sh
--undistort \"-0.00002,0.0000000004,0.00006,0.00006\" -b \"0,50,1228,247,1228,695,0,720\" --paf 7 --arcmin 45 --legmax 80 --legmin 10 --legvar 30 --areamin 100 --areamax 1000 --expected 333
```
## 2. Olathe
### Shelf 0
```sh
--undistort \"-0.00002,0.0000000004,0.00006,0.00006\" -b \"0,0,1280,0,1280,650,0,650\" --paf 7 --arcmin 45 --legmax 80 --legmin 10 --legvar 30 --areamin 100 --areamax 1000 --expected 333
```
### Shelf 1
```sh
--undistort \"-0.00002,0.0000000004,0.00006,0.00006\" -b \"0,0,1280,0,1280,650,0,650\" --paf 7 --arcmin 45 --legmax 80 --legmin 10 --legvar 30 --areamin 100 --areamax 1000 --expected 333
```
### Shelf 2
```sh
--undistort \"-0.00002,0.0000000004,0.00006,0.00006\" -b \"0,0,1280,0,1280,650,0,650\" --paf 7 --arcmin 45 --legmax 80 --legmin 10 --legvar 30 --areamin 100 --areamax 1000 --expected 333
```
### Shelf 3
```sh
--undistort \"-0.00002,0.0000000004,0.00006,0.00006\" -b \"0,50,1228,247,1228,695,0,720\" --paf 7 --arcmin 45 --legmax 80 --legmin 10 --legvar 30 --areamin 100 --areamax 1000 --expected 333
```
## 3. Target A
### Shelf 0
```sh
--undistort \"-0.00002,0.0000000004,0.00006,0.00006\" -b \"0,0,1920,0,1920,1080,0,1080\" --paf 7 --arcmin 45 --legmax 80 --legmin 10 --legvar 30 --areamin 100 --areamax 1000 --expected 270
```
### Shelf 1
```sh
--undistort \"-0.00002,0.0000000004,0.00006,0.00006\" -b \"0,0,1920,0,1920,1080,0,1080\" --paf 7 --arcmin 45 --legmax 80 --legmin 10 --legvar 30 --areamin 100 --areamax 1000 --expected 270
```
### Shelf 2
```sh
--undistort \"-0.00002,0.0000000004,0.00006,0.00006\" -b \"0,0,1920,0,1920,1080,0,1080\" --paf 7 --arcmin 45 --legmax 80 --legmin 10 --legvar 30 --areamin 100 --areamax 1000 --expected 280
```
### Shelf 3
```sh
--undistort \"-0.00002,0.0000000004,0.00006,0.00006\" -b \"0,0,1920,0,1920,1080,0,1080\" --paf 7 --arcmin 45 --legmax 80 --legmin 10 --legvar 30 --areamin 100 --areamax 1000 --expected 280
```
## 3. Target B
### Shelf 0
```sh
--undistort \"-0.00002,0.0000000004,0.00006,0.00006\" -b \"0,0,1920,0,1920,1080,0,1080\" --paf 7 --arcmin 45 --legmax 80 --legmin 10 --legvar 30 --areamin 100 --areamax 1000 --expected 270
```
### Shelf 1
```sh
--undistort \"-0.00002,0.0000000004,0.00006,0.00006\" -b \"0,0,1920,0,1920,1080,0,1080\" --paf 7 --arcmin 45 --legmax 80 --legmin 10 --legvar 30 --areamin 100 --areamax 1000 --expected 280
```
### Shelf 2
```sh
--undistort \"-0.00002,0.0000000004,0.00006,0.00006\" -b \"0,0,1920,0,1920,1080,0,1080\" --paf 7 --arcmin 45 --legmax 80 --legmin 10 --legvar 30 --areamin 100 --areamax 1000 --expected 280
```
### Shelf 3
```sh
--undistort \"-0.00002,0.0000000004,0.00006,0.00006\" -b \"0,0,1920,0,1920,1080,0,1080\" --paf 7 --arcmin 45 --legmax 80 --legmin 10 --legvar 30 --areamin 100 --areamax 1000 --expected 300
```