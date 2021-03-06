{-# LANGUAGE RecordWildCards, DataKinds #-}

module HSDFEdge where

-- imports
import CLaSH.Prelude
import Debug.Trace
import qualified Data.List as L

import HSDFTypes

-- ignore the most significant bit by shifting up and down
ptr2ind ptr = shiftR (shiftL ptr 1) 1


hsdfedge8 :: (Vec8 a, RdPtr, WrPtr) -> (a, Bool, Bool) -> ((Vec8 a, RdPtr, WrPtr), (a, Bool, Bool))
hsdfedge8 (elms, rptr, wptr) (datain, rd, wrt) = ((elms', rptr', wptr'), (dataout, canrd, canwrt))
    where
        elms' = if wrt then replace (ptr2ind wptr) datain elms else elms
        rptr' = if rd then rptr + 1 else rptr
        wptr' = if wrt then wptr + 1 else wptr
        dataout = elms !! (ptr2ind rptr)
        empty = rptr == wptr
        full = (msb rptr /= msb wptr) && (ptr2ind rptr == ptr2ind wptr)
        canrd = not empty
        canwrt = not full



hsdfedge8byteL = mealy hsdfedge8 (repeat 0 :: Vec 8 Byte, 0 :: Unsigned 4, 0 :: Unsigned 4)

-- Check whether the fifo contains the the element that is written and is not empty anymore
write_sim_res       = simulate hsdfedge8byteL [(66, False, True), (77, False, False), (88, False, False)]
write_sim_correct   = write_sim_res L.!! 1 == (66, True, True)

-- Write and and read: fifo should be empty again
write_read_sim_res       = simulate hsdfedge8byteL [(66, False, True), (77, True, False), (88, False, False)]
write_read_sim_correct   = write_read_sim_res L.!! 2 == (0, False, True)

-- Write 8 elements: fifo should be full
write8_sim_res       = simulate hsdfedge8byteL [(11, False, True), (22, False, True), (33, False, True), (44, False, True), (55, False, True), (66, False, True), (77, False, True), (88, False, True), (00, False, False)]
write8_sim_correct   = write8_sim_res L.!! 8 == (11, True, False)

-- Write and read 3 elements and verify their values
write3_read3_sim_res = simulate hsdfedge8byteL [(11, False, True), (22, False, True), (33, False, True), (44, True, False), (55, True, False), (66, True, False), (77, False, False)]
write3_read3_sim_correct = write3_read3_sim_res L.!! 3 == (11, True, True) && write3_read3_sim_res L.!! 4 == (22, True, True) && write3_read3_sim_res L.!! 5 == (33, True, True) && write3_read3_sim_res L.!! 6 == (0, False, True)



allSimsCorrect = write_sim_correct && write_read_sim_correct && write8_sim_correct && write3_read3_sim_correct


main = do
    putStrLn $ "All HSDF Edge tests correct: " L.++ (show allSimsCorrect)

topEntity = hsdfedge8byteL

